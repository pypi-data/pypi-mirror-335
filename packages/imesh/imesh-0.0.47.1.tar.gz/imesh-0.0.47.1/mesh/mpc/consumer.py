#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from abc import abstractmethod, ABC
from typing import Any

from mesh.kinds import Reference
from mesh.macro import spi
from mesh.mpc.invoker import Execution
from mesh.mpc.urn import URN


@spi(name="grpc")
class Consumer(ABC):
    HTTP = "http"
    GRPC = "grpc"
    TCP = "tcp"
    MQTT = "mqtt"

    """
    Service consumer with any protocol and codec.
    """

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def start(self):
        """
        Start the mesh broker.
        :return:
        """
        pass

    @abstractmethod
    async def consume(self, address: str, urn: URN, execution: Execution[Reference], inbound: bytes,
                      args: Any) -> bytes:
        """
        Consume the input payload.
        :param address: Remote address.
        :param urn: Actual uniform resource domain name.
        :param execution: Service reference.
        :param inbound: Input arguments.
        :param args: Additional arguments.
        :return: Output payload
        """
        pass
