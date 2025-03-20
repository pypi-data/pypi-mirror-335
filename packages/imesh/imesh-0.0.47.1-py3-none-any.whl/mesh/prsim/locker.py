#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from abc import ABC, abstractmethod

from mesh.macro import spi, mpi


@spi("mesh")
class Locker(ABC):

    @abstractmethod
    @mpi("mesh.locker.w.lock")
    async def lock(self, rid: str, timeout: int) -> bool:
        """
        Acquires the lock.
        :param rid:
        :param timeout: in mills
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.locker.w.unlock")
    async def unlock(self, rid: str):
        """
        Releases the lock.
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.locker.r.lock")
    async def read_lock(self, rid: str, timeout: int) -> bool:
        """
        Create a sample lock.
        :param rid:
        :param timeout:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.locker.r.unlock")
    async def read_unlock(self, rid: str):
        """
        Create a sample lock.
        :param rid:
        :return:
        """
        pass
