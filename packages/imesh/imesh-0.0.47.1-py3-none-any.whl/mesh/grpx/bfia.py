#
# Copyright (c) 2000, 2023, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from typing import Any

import grpc

import mesh.codec.tools as tools
from mesh.context import Mesh
from mesh.grpx.channels import GrpcChannels
from mesh.kinds import Reference
from mesh.mpc.invoker import Execution
from mesh.ptp.y_pb2 import PeekInbound, PopInbound, PushInbound, ReleaseInbound, TransportOutbound


class BfiaBinding:
    def __init__(self, urn: str, args: Any):
        if urn.startswith("peek.chan.mesh"):
            self.path = "/org.ppc.ptp.PrivateTransferTransport/peek"
            self.inbound = PeekInbound()
            self.inbound.topic = args.topic
            self.outbound = TransportOutbound
        elif urn.startswith("pop.chan.mesh"):
            self.path = "/org.ppc.ptp.PrivateTransferTransport/pop"
            self.inbound = PopInbound()
            self.inbound.topic = args.topic
            self.inbound.timeout = args.timeout
            self.outbound = TransportOutbound
        elif urn.startswith("push.chan.mesh"):
            self.path = "/org.ppc.ptp.PrivateTransferTransport/push"
            self.inbound = PushInbound()
            self.inbound.topic = args.topic
            self.inbound.payload = args.payload
            if args.metadata:
                for k, v in args.metadata.items():
                    self.inbound.metadata[k] = v
            self.outbound = TransportOutbound
        elif urn.startswith("release.chan.mesh"):
            self.path = "/org.ppc.ptp.PrivateTransferTransport/release"
            self.inbound = ReleaseInbound()
            self.inbound.topic = args.topic
            self.inbound.timeout = args.timeout
            self.outbound = TransportOutbound
        else:
            self.path = ""
            self.inbound = None
            self.outbound = None

    def encode(self, _: bytes):
        return self.inbound.SerializeToString()

    def decode(self, buffer: bytes):
        out = self.outbound()
        out.ParseFromString(buffer)
        v = "{" + f'"code":"{out.code}","message":"{out.message}","content":"{tools.b64encode(out.payload)}"' + "}"
        return v.encode('utf-8')


async def bfia_consume(address: str, binding: BfiaBinding, execution: Execution[Reference], inbound: bytes,
                       channel: GrpcChannels) -> bytes:
    urn = Mesh.context().get_urn()
    try:
        Mesh.context().rewrite_urn("")
        ct = Mesh.context().get_attribute(Mesh.TIMEOUT)
        timeout = (ct if ct else execution.schema().timeout) / 1000
        channel = channel.create_if_absent(address)
        conn = channel.unary_unary(binding.path, binding.encode, binding.decode)
        return await conn(inbound, timeout=timeout, metadata=[], wait_for_ready=True, compression=grpc.Compression.Gzip)
    finally:
        Mesh.context().rewrite_urn(urn)
