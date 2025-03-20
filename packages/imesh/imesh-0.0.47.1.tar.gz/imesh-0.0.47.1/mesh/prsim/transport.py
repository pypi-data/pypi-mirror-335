#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from abc import abstractmethod, ABC
from typing import Generic, Dict

from mesh.macro import spi, mpi, T


@spi("mesh")
class Transport(ABC, Generic[T]):
    """
    Private compute data channel in async and blocking mode.
    """

    MESH = "mesh"
    GRPC = "grpc"

    @abstractmethod
    @mpi("mesh.chan.open")
    async def open(self, session_id: str, metadata: Dict[str, str]) -> "Session":
        """
        Open a channel session.
        :param session_id:  node id or inst id
        :param metadata channel metadata
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.chan.close")
    async def close(self, timeout: int):
        """
        Close the channel.
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.chan.roundtrip")
    async def roundtrip(self, payload: bytes, metadata: Dict[str, str]) -> bytes:
        """
        Roundtrip with the channel.
        :param payload:
        :param metadata:
        :return:
        """
        pass


@spi("mesh")
class Session(ABC, Generic[T]):
    """
    Remote queue in async and blocking mode.
    """

    @abstractmethod
    @mpi("mesh.chan.peek")
    async def peek(self, topic: str = "") -> bytes:
        """
        Retrieves, but does not remove, the head of this queue,
        or returns None if this queue is empty.
        :param topic: message topic
        :return: the head of this queue, or None if this queue is empty
        :return:
        """
        pass

    @abstractmethod
    @mpi(name="mesh.chan.pop", timeout=120 * 1000)
    async def pop(self, timeout: int, topic: str = "") -> bytes:
        """
        Retrieves and removes the head of this queue,
        or returns None if this queue is empty.
        :param timeout: timeout in mills.
        :param topic: message topic
        :return: the head of this queue, or None if this queue is empty
        """
        pass

    @abstractmethod
    @mpi("mesh.chan.push")
    async def push(self, payload: bytes, metadata: Dict[str, str], topic: str = ""):
        """
        Inserts the specified element into this queue if it is possible to do
        so immediately without violating capacity restrictions.
        When using a capacity-restricted queue, this method is generally
        preferable to add, which can fail to insert an element only
        by throwing an exception.
        :param payload: message payload
        :param metadata: Message metadata
        :param topic: message topic
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.chan.release")
    async def release(self, timeout: int, topic: str = ""):
        """
        Close the channel session.
        :param timeout:
        :param topic: message topic
        :return:
        """
        pass
