#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import List

from mesh.context import MeshKey
from mesh.environ import Mode
from mesh.kinds import Route, Environ, Versions, Paging, Page, Institution
from mesh.macro import spi
from mesh.mpc import ServiceProxy, Mesh
from mesh.prsim import Network


@spi("mesh")
class MeshNetwork(Network):

    def __init__(self):
        self.proxy = ServiceProxy.default_proxy(Network)
        self.environ_key = MeshKey("mesh-environ", Environ)
        self.environ: Environ = Environ.default() if Mode.Isolate.enable() else None

    async def get_environ(self) -> Environ:
        if self.environ:
            return self.environ
        if Mesh.context().get_attribute(self.environ_key):
            return Mesh.context().get_attribute(self.environ_key)
        environ = Environ.default()
        Mesh.context().set_attribute(self.environ_key, environ)

        self.environ = await Mesh.context_safe(self.get_environ_safe())
        return self.environ

    async def get_environ_safe(self) -> Environ:
        Mesh.context().get_principals().clear()
        return await self.proxy.get_environ()

    async def accessible(self, route: Route) -> bool:
        return await self.proxy.accessible(route)

    async def refresh(self, routes: List[Route]):
        return await self.proxy.refresh(routes)

    async def get_route(self, node_id: str) -> Route:
        return await self.proxy.get_route(node_id)

    async def get_routes(self) -> List[Route]:
        return await self.proxy.get_routes()

    async def get_domains(self) -> List[Route]:
        return await self.proxy.get_domains()

    async def put_domains(self, domains: List[Route]):
        return await self.proxy.put_domains(domains)

    async def weave(self, route: Route) -> None:
        return await self.proxy.weave(route)

    async def ack(self, route: Route) -> None:
        return await self.proxy.ack(route)

    async def disable(self, node_id: str) -> None:
        return await self.proxy.disable(node_id)

    async def enable(self, node_id: str) -> None:
        return await self.proxy.enable(node_id)

    async def index(self, index: Paging) -> Page[Route]:
        return await self.proxy.index(index)

    async def version(self, node_id: str) -> Versions:
        return await self.proxy.version(node_id)

    async def instx(self, index: Paging) -> Page[Institution]:
        return await self.proxy.instx(index)

    async def instr(self, institutions: List[Institution]) -> str:
        return await self.proxy.instr(institutions)

    async def ally(self, node_ids: List[str]) -> None:
        await self.proxy.ally(node_ids)

    async def disband(self, node_ids: List[str]) -> None:
        await self.proxy.disband(node_ids)
