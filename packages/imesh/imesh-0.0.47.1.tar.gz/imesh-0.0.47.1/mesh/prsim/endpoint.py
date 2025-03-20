#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from abc import ABC, abstractmethod
from typing import Generic

from mesh.macro import mpi, spi, T, A


@spi("mesh")
class Endpoint(ABC):
    """
    Like subscriber but synchronized and has return value. For any extension.
    """

    @abstractmethod
    @mpi("${mesh.uname}")
    async def fuzzy(self, buff: bytes) -> bytes:
        """
        Invoke endpoint.
        :param buff:
        :return:
        """
        pass


@spi("mesh")
class EndpointSticker(ABC, Generic[T, A]):
    """
    Like subscriber but synchronized and has return value. For any extension.
    """

    @abstractmethod
    async def stick(self, varg: T) -> A:
        """
        Invoke endpoint.
        :param varg:
        :return:
        """
        pass
