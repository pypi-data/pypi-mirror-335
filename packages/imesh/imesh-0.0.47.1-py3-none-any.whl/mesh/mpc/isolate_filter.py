#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from typing import Any

from mesh.environ import Mode
from mesh.macro import spi
from mesh.mpc.filter import Filter, Invoker, Invocation, CONSUMER


@spi(name="isolate", pattern=CONSUMER, priority=100 - (1 << 32))
class IsolateFilter(Filter):

    async def invoke(self, invoker: Invoker, invocation: Invocation) -> Any:
        if Mode.Isolate.enable() and self.is_isolate(invocation):
            return None
        return await invoker.run(invocation)

    @staticmethod
    def is_isolate(invocation: Invocation) -> bool:
        return "mesh.net.environ,mesh.registry.put,mesh.registry.puts,mesh.registry.remove".__contains__(
            invocation.get_urn().name)
