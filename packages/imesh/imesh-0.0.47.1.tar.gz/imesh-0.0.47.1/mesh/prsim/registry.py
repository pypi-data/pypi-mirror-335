#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from abc import ABC, abstractmethod
from typing import List

from mesh.kinds import Registration
from mesh.macro import mpi, spi


@spi("mesh")
class Registry(ABC):

    @abstractmethod
    @mpi("mesh.registry.put")
    async def register(self, registration: Registration):
        """
        Register metadata to mesh graph database.
        :param registration:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.registry.puts")
    async def registers(self, registrations: List[Registration]):
        """
        Register metadata to mesh graph database.
        :param registrations:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.registry.remove")
    async def unregister(self, registration: Registration):
        """
        Unregister metadata from mesh graph database.
        :param registration:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.registry.export")
    async def export(self, kind: str) -> List[Registration]:
        """
        Export register metadata of mesh graph database.
        :param kind:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.registry.services")
    async def services(self, service: str) -> List[Registration]:
        """
        Service metadata of mesh graph database with given service.
        :param service:
        :return:
        """
        pass
