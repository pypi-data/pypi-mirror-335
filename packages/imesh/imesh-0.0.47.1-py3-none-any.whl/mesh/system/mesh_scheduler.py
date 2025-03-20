#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import List

from mesh.kinds import Topic, Timeout
from mesh.macro import spi
from mesh.mpc import ServiceProxy
from mesh.prsim import Scheduler


@spi("mesh")
class MeshScheduler(Scheduler):

    def __init__(self):
        self.remote = ServiceProxy.default_proxy(Scheduler)

    async def timeout(self, timeout: Timeout, duration: int) -> str:
        return await self.remote.timeout(timeout, duration)

    async def cron(self, cron: str, binding: Topic) -> str:
        return await self.remote.cron(cron, binding)

    async def period(self, duration: int, binding: Topic) -> str:
        return await self.remote.period(duration, binding)

    async def dump(self) -> List[str]:
        return await self.remote.dump()

    async def cancel(self, task_id: str) -> bool:
        return await self.remote.cancel(task_id)

    async def stop(self, task_id: str) -> bool:
        return await self.remote.stop(task_id)

    async def emit(self, topic: Topic) -> bool:
        return await self.remote.emit(topic)

    async def shutdown(self, duration: int) -> bool:
        return await self.remote.shutdown(duration)
