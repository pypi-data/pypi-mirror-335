#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from abc import ABC, abstractmethod
from typing import Type, Any

from mesh.kinds import Entity
from mesh.macro import mpi, spi, T


@spi("mesh")
class KV(ABC):

    @abstractmethod
    @mpi("mesh.kv.get")
    async def get(self, key: str) -> Entity:
        """
        Get the value from kv store.
        :param key:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.kv.put")
    async def put(self, key: str, value: Entity):
        """
        Put the value to kv store.
        :param key:
        :param value:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.kv.remove")
    async def remove(self):
        """
        Remove the kv store.
        :return:
        """
        pass

    async def get_with_type(self, key: str, kind: Type[T]) -> T:
        """
        Get by codec.
        :param key:
        :param kind:
        :return:
        """
        entity = await self.get(key)
        return entity.try_read_object(kind) if entity else None

    async def put_object(self, key: str, value: Any):
        """
        Put by codec.
        :param key:
        :param value:
        :return:
        """
        await self.put(key, Entity.wrap(value))
