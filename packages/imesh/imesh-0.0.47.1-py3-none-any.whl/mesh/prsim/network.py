#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from abc import abstractmethod, ABC
from typing import List

from mesh.kinds import Environ, Route, Versions, Paging, Page, Institution
from mesh.macro import mpi, spi


@spi("mesh")
class Network(ABC):

    @abstractmethod
    @mpi("mesh.net.environ")
    async def get_environ(self) -> Environ:
        """
        Get the meth network environment fixed information.
        :return: Fixed system information.
        """
        pass

    @abstractmethod
    @mpi("mesh.net.accessible")
    async def accessible(self, route: Route) -> bool:
        """
        Check the mesh network is accessible.
        :param route: Network route.
        :return: true is accessible.
        """
        pass

    @abstractmethod
    @mpi("mesh.net.refresh")
    async def refresh(self, routes: List[Route]):
        """
        Refresh the routes to mesh network.
        :param routes: Network routes.
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.net.edge")
    async def get_route(self, node_id: str) -> Route:
        """
        GetNetRoute the network edge routes.
        :param node_id: node id
        :return: edge routes
        """
        pass

    @abstractmethod
    @mpi("mesh.net.edges")
    async def get_routes(self) -> List[Route]:
        """
        GetNetRoute the network edge routes.
        :return: edge routes
        """
        pass

    @abstractmethod
    @mpi("mesh.net.domains")
    async def get_domains(self) -> List[Route]:
        """
        GetNetDomain the network domains.
        :return: net domains
        """
        pass

    @abstractmethod
    @mpi("mesh.net.resolve")
    async def put_domains(self, domains: List[Route]):
        """
        Put the network domains.
        """
        pass

    @abstractmethod
    @mpi("mesh.net.weave")
    async def weave(self, route: Route) -> None:
        """
        Weave the network.
        :param route:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.net.ack")
    async def ack(self, route: Route) -> None:
        """
        Acknowledge the network.
        :param route:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.net.disable")
    async def disable(self, node_id: str) -> None:
        """
        Disable the network.
        :param node_id:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.net.enable")
    async def enable(self, node_id: str) -> None:
        """
        Enable the network.
        :param node_id:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.net.index")
    async def index(self, index: Paging) -> Page[Route]:
        """
        Index the network edges.
        :param index:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.net.version")
    async def version(self, node_id: str) -> Versions:
        """
        Network environment version.
        :param node_id:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.net.instx")
    async def instx(self, index: Paging) -> Page[Institution]:
        """
        Network institutions.
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.net.instr")
    async def instr(self, institutions: List[Institution]) -> str:
        """
        Network institutions.
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.net.ally")
    async def ally(self, node_ids: List[str]) -> None:
        """
        Network form alliance.
        """
        pass

    @abstractmethod
    @mpi("mesh.net.disband")
    async def disband(self, node_ids: List[str]) -> None:
        """
        Network quit alliance.
        """
        pass
