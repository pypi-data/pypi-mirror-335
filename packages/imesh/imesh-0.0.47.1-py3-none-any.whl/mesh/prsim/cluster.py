#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from abc import abstractmethod, ABC

from mesh.macro import spi, mpi


@spi(name="mesh")
class Cluster(ABC):

    @abstractmethod
    @mpi("mesh.cluster.election")
    async def election(self, buff: bytes) -> bytes:
        """
        Election will election leader of instances.
        :param buff:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.cluster.leader")
    async def is_leader(self) -> bool:
        """
        IsLeader if same level.
        :return:
        """
        pass
