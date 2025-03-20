#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from mesh.macro import spi
from mesh.prsim import RuntimeHook


@spi("mesh")
class MeshRuntimeHook(RuntimeHook):

    async def start(self):
        """"""
        pass

    async def stop(self):
        """"""
        pass

    async def refresh(self):
        """"""
        pass

    async def wait(self):
        """"""
        pass
