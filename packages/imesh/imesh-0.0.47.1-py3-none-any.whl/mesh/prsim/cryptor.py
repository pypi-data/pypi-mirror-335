#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from abc import ABC, abstractmethod
from typing import Dict

from mesh.macro import spi, mpi


@spi("mesh")
class Cryptor(ABC):

    @abstractmethod
    @mpi("mesh.crypt.encrypt")
    async def encrypt(self, buff: bytes, features: Dict[str, str]) -> bytes:
        """
        Encrypt binary to encrypted binary.
        :param buff:
        :param features:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.crypt.decrypt")
    async def decrypt(self, buff: bytes, features: Dict[str, str]) -> bytes:
        """
        Decrypt binary to decrypted binary.
        :param buff:
        :param features:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.crypt.hash")
    async def hash(self, buff: bytes, features: Dict[str, str]) -> bytes:
        """
        Hash compute the hash value.
        :param buff:
        :param features:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.crypt.sign")
    async def hash(self, buff: bytes, features: Dict[str, str]) -> bytes:
        """
        Sign compute the signature value.
        :param buff:
        :param features:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.crypt.verify")
    async def verify(self, buff: bytes, features: Dict[str, str]) -> bytes:
        """
        Verify the signature value.
        :param buff:
        :param features:
        :return:
        """
        pass
