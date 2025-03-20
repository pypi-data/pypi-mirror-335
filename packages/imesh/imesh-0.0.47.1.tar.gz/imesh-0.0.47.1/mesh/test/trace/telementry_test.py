#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

import os
import time
import unittest

import mesh.asm as asm
import mesh.log as log
from mesh.macro import mpi
from mesh.prsim import Network
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

resource = Resource(attributes={SERVICE_NAME: "gaia-mpi"})

# os.environ.setdefault("MESH_MODE", "4")
os.environ.setdefault("MESH_ADDRESS", "10.99.56.33")
os.environ.setdefault("MESH_NAME", "pandoroo")

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://10.99.56.76:4318/v1/traces"))
provider.add_span_processor(processor)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(os.environ.get("MESH_NAME"))


class TestGrpc(unittest.TestCase):

    @mpi
    def network(self) -> Network:
        """"""
        pass

    def test_get_environ(self):
        with tracer.start_as_current_span("asm.init"):
            asm.init()
            with tracer.start_as_current_span("get_environ"):
                environ = self.network.get_environ()
                assert environ
                log.info(environ.node_id)
            log.info("asm.init done")
        log.info("test_get_environ done")


if __name__ == '__main__':
    unittest.main()
    time.sleep(15)
    # curl http://10.99.56.76:3100/api/traces/011e8df9a141e7c4c952a15643c0c956
    # tempo service
