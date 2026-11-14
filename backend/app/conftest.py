import os

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# Set before app.main is imported: tests keep their spans in memory instead of
# sending them to a collector that does not exist here.
os.environ["OTEL_TRACES_EXPORTER"] = "none"
os.environ.pop("OTEL_SDK_DISABLED", None)

_exporter = InMemorySpanExporter()


@pytest.fixture
def finished_spans():
    import app.main  # noqa: F401  installs the tracer provider

    provider = trace.get_tracer_provider()
    if not getattr(provider, "_test_exporter_added", False):
        provider.add_span_processor(SimpleSpanProcessor(_exporter))
        provider._test_exporter_added = True
    _exporter.clear()
    return _exporter.get_finished_spans
