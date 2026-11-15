import json
import logging
import os
import sys
import time
from datetime import UTC, datetime

from fastapi import FastAPI, Request, Response
from fastapi.telemetry import TelemetryConfig
from opentelemetry import trace
from prometheus_client import CONTENT_TYPE_LATEST, Histogram, generate_latest
from starlette.types import ASGIApp, Message, Receive, Scope, Send

GATEWAY_ENDPOINT = "http://otelcol-gateway.observability.svc:4317"
# Probes and scrapes arrive every few seconds: observing them would bury the
# real traffic in traces, metrics and logs.
UNOBSERVED_PATHS = ("/health", "/metrics")

REQUEST_DURATION = Histogram(
    "http_server_request_duration_seconds",
    "Duration of the HTTP requests served by the API, by route template.",
    ["method", "route", "status"],
)

request_logger = logging.getLogger("app.request")

# color_message is uvicorn's copy of the message with terminal colour codes.
_STANDARD_RECORD_FIELDS = frozenset(vars(logging.makeLogRecord({}))) | {
    "message",
    "asctime",
    "color_message",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        entry.update(
            (key, value) for key, value in vars(record).items() if key not in _STANDARD_RECORD_FIELDS
        )
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def _add_trace_context(factory):
    def make_record(*args, **kwargs) -> logging.LogRecord:
        record = factory(*args, **kwargs)
        span_context = trace.get_current_span().get_span_context()
        if span_context.is_valid:
            record.trace_id = format(span_context.trace_id, "032x")
            record.span_id = format(span_context.span_id, "016x")
        return record

    make_record.adds_trace_context = True
    return make_record


def configure_logging() -> None:
    """JSON on stdout, one object per line, with the trace of the current request."""
    factory = logging.getLogRecordFactory()
    if not getattr(factory, "adds_trace_context", False):
        logging.setLogRecordFactory(_add_trace_context(factory))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

    # uvicorn installs its own text handlers before importing the app.
    for name in ("uvicorn", "uvicorn.error"):
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    # Replaced by the app.request line, which has the route and the trace.
    logging.getLogger("uvicorn.access").disabled = True


class RequestTelemetryMiddleware:
    """Records every request in the RED histogram and logs it once."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] in UNOBSERVED_PATHS:
            await self.app(scope, receive, send)
            return

        status = 500
        start = time.perf_counter()

        async def send_and_keep_status(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_and_keep_status)
        finally:
            duration = time.perf_counter() - start
            # The template, never the raw path: /items/1, /items/2... would each
            # become a new series.
            route = getattr(scope.get("route"), "path", None) or "unmatched"
            REQUEST_DURATION.labels(scope["method"], route, str(status)).observe(duration)
            request_logger.info(
                "%s %s %s",
                scope["method"],
                route,
                status,
                extra={
                    "method": scope["method"],
                    "route": route,
                    "path": scope["path"],
                    "status": status,
                    "duration_ms": round(duration * 1000, 1),
                },
            )


async def metrics(_: Request) -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def configure_tracing() -> TelemetryConfig:
    """Sets up the OpenTelemetry SDK and returns the settings for FastAPI(telemetry=...).

    FastAPI traces requests natively; httpx calls and PostgreSQL queries become child spans.
    """
    if os.getenv("OTEL_SDK_DISABLED", "").lower() == "true":
        return {"tracing": False, "metrics": False, "logs": False}

    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
    from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

    # Only the service identity: the collector derives the pod, namespace and
    # project from the connection and drops any k8s.* or project attribute a
    # client sends, so Resource.create() and OTEL_RESOURCE_ATTRIBUTES are not used.
    resource = Resource(
        {
            SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "backend"),
            SERVICE_VERSION: os.getenv("APP_VERSION", "dev"),
        }
    )
    sampler = None
    if "OTEL_TRACES_SAMPLER" not in os.environ:
        sampler = ParentBased(TraceIdRatioBased(float(os.getenv("OTEL_TRACES_SAMPLER_ARG", "1.0"))))
    provider = TracerProvider(resource=resource, sampler=sampler)

    if os.getenv("OTEL_TRACES_EXPORTER", "otlp") != "none":
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        endpoint = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT") or os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT", GATEWAY_ENDPOINT
        )
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))

    trace.set_tracer_provider(provider)
    HTTPXClientInstrumentor().instrument(tracer_provider=provider)
    # At the driver rather than SQLAlchemy: the SQLAlchemy instrumentation does
    # not support SQLAlchemy 2.1 yet. SQLite, used only locally, is not traced.
    PsycopgInstrumentor().instrument(tracer_provider=provider)

    return {
        "tracer_provider": provider,
        "tracing": True,
        # RED metrics come from prometheus-client on /metrics, logs from stdout.
        "metrics": False,
        "logs": False,
        # One span per request; dependency and serialization spans are noise here.
        "operation_spans": False,
        "exclude": lambda scope: scope.get("path") in UNOBSERVED_PATHS,
    }


def instrument(app: FastAPI) -> None:
    app.add_middleware(RequestTelemetryMiddleware)
    app.add_route("/metrics", metrics, include_in_schema=False)
