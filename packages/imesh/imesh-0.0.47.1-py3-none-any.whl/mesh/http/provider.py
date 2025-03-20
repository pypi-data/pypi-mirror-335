#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import Any

import mesh.log as log
from mesh.macro import spi
from mesh.mpc import Provider


@spi("http")
class HTTPProvider(Provider):

    def __init__(self):
        self.address = ""

    async def start(self, address: str, tc: Any):
        self.address = address
        log.info(f"Listening and serving HTTP 1.x on {address}")

    async def close(self):
        log.info(f"Graceful stop HTTP 1.x serving on {self.address}")

    async def wait(self):
        """"""
        pass
