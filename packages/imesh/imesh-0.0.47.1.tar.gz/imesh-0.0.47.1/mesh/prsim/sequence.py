#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from abc import ABC, abstractmethod
from typing import List

from mesh.macro import spi, mpi


@spi("mesh")
class Sequence(ABC):

    @abstractmethod
    @mpi("mesh.sequence.next")
    async def next(self, kind: str, length: int) -> str:
        """
        Generate a unique number in network.
        :param kind:
        :param length:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.sequence.section")
    async def section(self, kind: str, size: int, length: int) -> List[str]:
        """
        Generate some unique number in network as s section.
        :param kind:
        :param size:
        :param length:
        :return:
        """
        pass
