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
import mesh.telemetry as telemetry
from mesh.macro import mpi
from mesh.prsim import Network, Locker

os.environ.setdefault("MESH_MODE", "")
os.environ.setdefault("MESH_ADDRESS", "")
os.environ.setdefault("MESH_NAME", "abc")
os.environ.setdefault("OPEN_TELEMETRY_ENDPOINT", "http://localhost:4317")


class TestMTelemetry(unittest.TestCase):

    @mpi
    def network(self) -> Network:
        """"""
        pass

    @mpi
    def locker(self) -> Locker:
        """"""
        pass

    def test_get_environ(self):
        spn = telemetry.get_current_span()
        print(f'{spn}')
        with telemetry.tracer.start_as_current_span("asm.init"):
            asm.init()
            for x in range(1, 10):
                with telemetry.tracer.start_as_current_span("get_environ"):
                    environ = self.network.get_environ()
                    assert environ
                    log.info(f'{environ.node_id}-{x}')
                    lockable = self.locker.lock(f'{x}-read-lock', 10)
                    log.info(f'{lockable}-{x}')
            log.info("asm.init done")
        log.info("test_get_environ done")


if __name__ == '__main__':
    # atta = {}
    # atta['mesh-telemetry-trace-id'] = 'e76c7c2efa4c33e794cc00e6d9a9aae8'
    # telemetry.build_via_remote(atta, 'test1')
    unittest.main()
    time.sleep(5)
    # curl http://10.99.56.76:3100/api/traces/011e8df9a141e7c4c952a15643c0c956
    # tempo service
