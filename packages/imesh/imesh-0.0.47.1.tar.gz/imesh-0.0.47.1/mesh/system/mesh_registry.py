#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import List

from mesh.kinds import Registration
from mesh.macro import spi
from mesh.mpc import ServiceProxy
from mesh.prsim import Registry


@spi("mesh")
class MeshRegistry(Registry):

    def __init__(self):
        self.proxy = ServiceProxy.default_proxy(Registry)

    async def register(self, registration: Registration):
        return await self.proxy.register(registration)

    async def registers(self, registrations: List[Registration]):
        return await self.proxy.registers(registrations)

    async def unregister(self, registration: Registration):
        return await self.proxy.unregister(registration)

    async def export(self, kind: str) -> List[Registration]:
        return await self.proxy.export(kind)

    async def services(self, service: str) -> List[Registration]:
        return await self.proxy.services(service)