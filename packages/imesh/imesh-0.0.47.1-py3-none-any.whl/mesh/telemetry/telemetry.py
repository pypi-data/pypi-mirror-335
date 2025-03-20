#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import (
    TracerProvider,
)
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    BatchSpanProcessor,
    SpanExporter,
    SpanProcessor,
)
from opentelemetry.sdk.trace.sampling import ALWAYS_ON

from mesh.environ import System


class MeshTelemetry:

    def __init__(self):
        self.__tracer__ = None

    def get_tracer(self, service_name: str = 'gaia-tracer', enable_std: bool = False):
        if self.__tracer__:
            return self.__tracer__
        if not System.environ().enable_telemetry():
            self.__tracer__ = trace.get_tracer_provider()
            return self.__tracer__
        # Service name is required for most backends
        resource = Resource(attributes={
            SERVICE_NAME: service_name
        })
        provider = TracerProvider(resource=resource, sampler=ALWAYS_ON)

        if enable_std:
            std_processor = SimpleSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(std_processor)

        if System.environ().get_telemetry_protocol() == 'http':
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            span_exporter = OTLPSpanExporter(endpoint=f'{System.environ().get_telemetry_endpoint()}/v1/traces')
            provider.add_span_processor(self._get_span_process(span_exporter))
        else:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            span_exporter = OTLPSpanExporter(endpoint=System.environ().get_telemetry_endpoint(),
                                             insecure=True)
            provider.add_span_processor(self._get_span_process(span_exporter))

        trace.set_tracer_provider(provider)
        self.__tracer__ = provider
        return self.__tracer__

    def _get_span_process(self, span_exporter: SpanExporter) -> SpanProcessor:
        if System.environ().get_telemetry_proc_type() == 'batch':
            return BatchSpanProcessor(span_exporter=span_exporter)
        else:
            return SimpleSpanProcessor(span_exporter=span_exporter)
