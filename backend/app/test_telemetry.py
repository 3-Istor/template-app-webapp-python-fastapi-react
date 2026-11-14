import json
import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import telemetry
from app.main import app

client = TestClient(app)


def test_metrics_exposes_the_request_histogram_by_route_template():
    client.get("/api/hello/alice")

    body = client.get("/metrics").text

    assert (
        'http_server_request_duration_seconds_count{method="GET",route="/api/hello/{name}",status="200"}'
        in body
    )
    assert "alice" not in body


def test_metrics_groups_unknown_paths_under_one_route():
    client.get("/no/such/page/123")

    body = client.get("/metrics").text

    assert 'route="unmatched",status="404"' in body
    assert "/no/such/page" not in body


def test_metrics_exposes_the_example_business_counter():
    client.get("/api/hello")

    body = client.get("/metrics").text

    assert "app_greetings_total" in body


def test_request_produces_one_span_named_after_the_route(finished_spans):
    client.get("/api/hello/bob")

    spans = finished_spans()
    assert [(span.name, span.attributes.get("http.route")) for span in spans] == [
        ("GET /api/hello/{name}", "/api/hello/{name}")
    ]


def test_span_resource_carries_only_the_service_identity(finished_spans):
    client.get("/api/hello")

    (span,) = finished_spans()
    assert set(span.resource.attributes) == {"service.name", "service.version"}


def test_health_and_metrics_produce_no_span(finished_spans):
    client.get("/health")
    client.get("/metrics")

    assert [s.name for s in finished_spans()] == []


def test_request_log_line_carries_the_current_trace_id(finished_spans, caplog):
    caplog.set_level(logging.INFO, logger="app.request")

    client.get("/api/hello")

    (span,) = finished_spans()
    (record,) = [r for r in caplog.records if r.name == "app.request"]
    line = json.loads(telemetry.JsonFormatter().format(record))
    assert (line["trace_id"], line["span_id"], line["route"]) == (
        format(span.context.trace_id, "032x"),
        format(span.context.span_id, "016x"),
        "/api/hello",
    )


def test_log_line_outside_a_request_has_no_trace_id():
    record = logging.getLogger("app.test").makeRecord(
        "app.test", logging.INFO, __file__, 1, "outside", (), None
    )

    line = json.loads(telemetry.JsonFormatter().format(record))

    assert "trace_id" not in line


def test_tracing_is_off_when_the_sdk_is_disabled(finished_spans, monkeypatch):
    monkeypatch.setenv("OTEL_SDK_DISABLED", "true")
    other_app = FastAPI(telemetry=telemetry.configure_tracing())
    other_app.get("/ping")(lambda: {"ok": True})
    telemetry.instrument(other_app)

    response = TestClient(other_app).get("/ping")

    assert response.status_code == 200
    assert [s.name for s in finished_spans()] == []
