import random
import os
from flask import Flask, request
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

OTEL_EXPORTER_OTLP_ENDPOINT = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger-collector.observability.svc.cluster.local:4317")

trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "service-b"}))
)
otlp_exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

app = Flask(__name__)
tracer = trace.get_tracer(__name__)


@app.route("/")
def state():
    with tracer.start_as_current_span("service-b-handler") as span:
        value = request.args.get('value', 'unknown')
        result = random.randint(1, 500)
        
        span.set_attribute("component", "service-b")
        span.set_attribute("request.received_value", value)
        span.set_attribute("request.result", result)
        
        return {
            "service": "b",
            "received_value": value,
            "result": result,
            "message": "ok",
        }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)