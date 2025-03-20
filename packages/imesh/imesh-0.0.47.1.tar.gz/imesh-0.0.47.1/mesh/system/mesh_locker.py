#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from mesh.macro import spi
from mesh.mpc import ServiceProxy
from mesh.prsim import Locker


@spi("mesh")
class MeshLocker(Locker):

    def __init__(self):
        self.locker = ServiceProxy.default_proxy(Locker)

    async def lock(self, rid: str, timeout: int) -> bool:
        return await self.locker.lock(rid, timeout)

    async def unlock(self, rid: str):
        return await self.locker.unlock(rid)

    async def read_lock(self, rid: str, timeout: int) -> bool:
        return await self.locker.read_lock(rid, timeout)

    async def read_unlock(self, rid: str):
        return await self.locker.read_unlock(rid)
