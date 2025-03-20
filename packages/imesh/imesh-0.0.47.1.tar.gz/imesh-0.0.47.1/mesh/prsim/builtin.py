#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from abc import ABC, abstractmethod
from typing import Dict, List

from mesh.kinds import Versions
from mesh.macro import spi, mpi


@spi("mesh")
class Builtin(ABC):

    @abstractmethod
    @mpi("${mesh.name}.builtin.doc")
    async def doc(self, name: str, formatter: str) -> str:
        """
        Export the documents.
        :param name:
        :param formatter:
        :return:
        """
        pass

    @abstractmethod
    @mpi("${mesh.name}.builtin.version")
    async def version(self) -> Versions:
        """
        Get the builtin application version.
        :return:
        """
        pass

    @abstractmethod
    @mpi("${mesh.name}.builtin.debug")
    async def debug(self, features: Dict[str, str]):
        """
        LogLevel set the application log level.
        :return:
        """
        pass

    @abstractmethod
    @mpi("${mesh.name}.builtin.stats")
    async def stats(self, features: List[str]) -> Dict[str, str]:
        """
        Health check stats.
        :param features:
        :return:
        """
        pass

    @abstractmethod
    @mpi("${mesh.name}.builtin.fallback")
    async def fallback(self):
        """
        Fallback is fallback service
        """
        pass

    @abstractmethod
    @mpi("${mesh.name}.builtin.dump")
    async def dump(self, names: List[str]) -> Dict[str, str]:
        """
        Dump the application data.
        :param names:
        :return:
        """
        pass
