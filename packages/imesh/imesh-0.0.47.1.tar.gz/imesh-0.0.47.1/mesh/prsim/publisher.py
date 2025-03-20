#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from abc import ABC, abstractmethod
from typing import List, Any

from mesh.kinds.event import Event
from mesh.kinds.event import Topic
from mesh.kinds.principal import Principal
from mesh.macro import mpi, spi


@spi("mesh")
class Publisher(ABC):

    @abstractmethod
    @mpi("mesh.queue.publish")
    async def publish(self, events: List[Event]) -> List[str]:
        """
        Publish event to mesh.
        :param events:
        :return:
        """
        pass

    @abstractmethod
    @mpi("mesh.queue.broadcast")
    async def broadcast(self, events: List[Event]) -> List[str]:
        """
        Synchronized broadcast the event to all subscriber. This maybe timeout with to many subscriber.
        :param events: Event payload
        :return: Synchronized subscriber return value
        """
        pass

    async def publish_with_topic(self, binding: Topic, payload: Any) -> str:
        """
        Publish message to local node.
        :param binding:
        :param payload:
        :return:
        """
        event = await Event.new_instance(payload, binding)
        rs = await self.publish([event])
        return rs[0]

    async def unicast(self, binding: Topic, payload: Any, principal: Principal) -> str:
        """
        Unicast will publish to another node.
        :param binding:
        :param payload:
        :param principal:
        :return:
        """
        event = await Event.new_instance_with_target(payload, binding, principal)
        rs = await self.publish([event])
        return rs[0]

    async def multicast(self, binding: Topic, payload: Any, principals: List[Principal]) -> List[str]:
        """
        Multicast will publish event to principal groups.
        :param binding:
        :param payload:
        :param principals:
        :return:
        """
        events: List[Event] = []
        for principal in principals:
            events.append(await Event.new_instance_with_target(payload, binding, principal))
        return await self.publish(events)

    async def broadcast_with_topic(self, binding: Topic, payload: Any) -> List[str]:
        """
        Synchronized broadcast the event to all subscriber. This maybe timeout with to many subscriber.
        :param binding:
        :param payload:
        :return:
        """
        return await self.broadcast([await Event.new_instance(payload, binding)])
