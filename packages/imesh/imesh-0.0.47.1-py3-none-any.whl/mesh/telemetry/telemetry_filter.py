#
# Copyright (c) 2019, 2023, ducesoft and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import random
from typing import Dict, Any

import mesh.telemetry as telemetry
import mesh.tool as tool
from mesh.context import Mesh
from mesh.macro import spi
from mesh.mpc.filter import Filter, Invoker, Invocation, CONSUMER, PROVIDER
from mesh.prsim import Metadata
from mesh.prsim import RunMode

TELEMETRY_TRACE_ID = 'mesh-telemetry-trace-id'
TELEMETRY_SPAN_ID = "mesh-telemetry-span-id"


@spi(name="telemetryConsumer", pattern=CONSUMER, priority=50 - (1 << 32))
class TelemetryConsumerFilter(Filter):

    async def invoke(self, invoker: Invoker, invocation: Invocation) -> Any:
        if TELEMETRY_TRACE_ID not in invocation.get_attachments():
            invocation.get_attachments()[TELEMETRY_TRACE_ID] = hex(random.getrandbits(128))[2:]

        if not RunMode.TRACE.match(Mesh.context().get_run_mode()):
            return await invoker.run(invocation)

        attachments: Dict[str, str] = Mesh.context().get_attachments()
        if not telemetry.if_rebuild_span():
            return await invoker.run(invocation)
        with telemetry.build_via_remote(attachments, invocation.get_urn().string()):
            current_span = telemetry.get_current_span()
            current_span.set_attribute('mesh-trace-id', Mesh.context().get_trace_id())
            return await invoker.run(invocation)


@spi(name="telemetryProvider", pattern=PROVIDER, priority=(1 << 32) - 50)
class TelemetryProviderFilter(Filter):
    """
    recover telemetry context via mesh context for tracing
    """

    async def invoke(self, invoker: Invoker, invocation: Invocation) -> Any:
        if TELEMETRY_TRACE_ID not in invocation.get_attachments():
            invocation.get_attachments()[TELEMETRY_TRACE_ID] = hex(random.getrandbits(128))[2:]

        if not RunMode.TRACE.match(Mesh.context().get_run_mode()):
            return await invoker.run(invocation)

        attachments: Dict[str, str] = invocation.get_parameters().get_attachments()
        if not telemetry.if_rebuild_span():
            return await invoker.run(invocation)
        trace_id = attachments.get(Metadata.MESH_TRACE_ID.key(), tool.new_trace_id())
        with telemetry.build_via_remote(attachments, invocation.get_urn().string()):
            current_span = telemetry.get_current_span()
            current_span.set_attribute('mesh-trace-id', trace_id)
            return await invoker.run(invocation)
