#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import Any, List

from mesh.kinds import Document, Paging, Page
from mesh.macro import spi
from mesh.mpc import ServiceProxy
from mesh.prsim import DataHouse


@spi("mesh")
class MeshDataHouse(DataHouse):

    def __init__(self):
        self.proxy = ServiceProxy.default_proxy(DataHouse)

    async def writes(self, docs: List[Document]):
        return await self.proxy.writes(docs)

    async def write(self, doc: Document):
        return await self.proxy.write(doc)

    async def read(self, index: Paging) -> Page[Any]:
        return await self.proxy.read(index)

    async def indies(self, index: Paging) -> Page[Any]:
        return await self.proxy.indies(index)

    async def tables(self, index: Paging) -> Page[Any]:
        return await self.proxy.tables(index)
