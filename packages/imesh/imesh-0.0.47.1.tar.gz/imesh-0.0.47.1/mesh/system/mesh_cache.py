#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from mesh.kinds import CacheEntity
from mesh.macro import spi
from mesh.mpc import ServiceProxy
from mesh.prsim import Cache


@spi("mesh")
class MeshCache(Cache):

    def __init__(self):
        self.proxy = ServiceProxy.default_proxy(Cache)

    async def get(self, key: str) -> CacheEntity:
        return await self.proxy.get(key)

    async def put(self, cell: CacheEntity) -> None:
        return await self.proxy.put(cell)

    async def remove(self, key: str):
        return await self.proxy.remove(key)

    async def incr(self, key: str, value: int, duration: int) -> int:
        return await self.proxy.incr(key, value, duration)

    async def decr(self, key: str, value: int, duration: int) -> int:
        return await self.proxy.decr(key, value, duration)
