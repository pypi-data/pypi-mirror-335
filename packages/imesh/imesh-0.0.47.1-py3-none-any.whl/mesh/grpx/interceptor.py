#
# Copyright (c) 2000, 2099, ducesoft and/or its affiliates. All rights reserved.
# DUCESOFT PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import collections
from typing import Callable, Union, Awaitable, List, Tuple

import grpc
from grpc.aio import UnaryUnaryCall, UnaryStreamCall, StreamUnaryCall, StreamStreamCall
from grpc.aio._typing import ResponseIterableType, RequestType, ResponseType, RequestIterableType

import mesh.tool as tool
from mesh.mpc import Mesh
from mesh.prsim import Metadata


class ClientCallDetails(
    collections.namedtuple('_ClientCallDetails',
                           ('method', 'timeout', 'metadata', 'credentials',
                            'wait_for_ready', 'compression')), grpc.ClientCallDetails):
    pass


class MeshInterceptor:
    TKeys = [
        Metadata.MESH_INCOMING_PROXY,
        Metadata.MESH_OUTGOING_PROXY,
        Metadata.MESH_SUBSET,
        Metadata.MESH_VERSION,
        Metadata.MESH_TIMESTAMP,
        Metadata.MESH_RUN_MODE,
        # INC
        Metadata.MESH_TECH_PROVIDER_CODE,
        Metadata.MESH_TOKEN,
        Metadata.MESH_TARGET_NODE_ID,
        Metadata.MESH_TARGET_INST_ID,
        Metadata.MESH_SESSION_ID
    ]

    @staticmethod
    def context_metadata() -> List[Tuple[str, str]]:
        # python metadata must be lowercase
        attachments = Mesh.context().get_attachments()
        metadata = []
        Metadata.MESH_URN.append(metadata, Mesh.context().get_urn())
        Metadata.MESH_TRACE_ID.append(metadata, Mesh.context().get_trace_id())
        Metadata.MESH_SPAN_ID.append(metadata, Mesh.context().get_span_id())
        Metadata.MESH_FROM_INST_ID.append(metadata, Mesh.context().get_consumer().inst_id)
        Metadata.MESH_FROM_NODE_ID.append(metadata, Mesh.context().get_consumer().node_id)
        Metadata.MESH_INCOMING_HOST.append(metadata, f"{tool.get_mesh_name()}@{str(tool.get_mesh_runtime())}")
        Metadata.MESH_OUTGOING_HOST.append(metadata, attachments.get(Metadata.MESH_INCOMING_HOST.key(), ''))

        for mk in GrpcInterceptor.TKeys:
            mk.append(metadata, attachments.get(mk.key(), ''))

        return metadata

    @staticmethod
    def client_context(ctx):
        wait_for_ready = ctx.wait_for_ready if hasattr(ctx, 'wait_for_ready') else None
        compression = ctx.compression if hasattr(ctx, 'compression') else None
        credentials = ctx.credentials if hasattr(ctx, 'credentials') else None
        return ClientCallDetails(ctx.method, ctx.timeout, ctx.metadata, credentials, wait_for_ready, compression)

    @staticmethod
    def server_context(handler_call_details):
        pass


class GrpcInterceptor(MeshInterceptor,
                      grpc.ServerInterceptor,
                      grpc.StreamStreamClientInterceptor,
                      grpc.StreamUnaryClientInterceptor,
                      grpc.UnaryStreamClientInterceptor,
                      grpc.UnaryUnaryClientInterceptor, ):

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        return continuation(self.client_context(client_call_details), request_iterator)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        return continuation(self.client_context(client_call_details), request_iterator)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        return continuation(self.client_context(client_call_details), request)

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return continuation(self.client_context(client_call_details), request)

    def intercept_service(self, continuation, handler_call_details):
        self.server_context(handler_call_details)
        return continuation(handler_call_details)


class AsyncGrpcInterceptor(MeshInterceptor,
                           grpc.aio.ServerInterceptor,
                           grpc.aio.StreamStreamClientInterceptor,
                           grpc.aio.StreamUnaryClientInterceptor,
                           grpc.aio.UnaryStreamClientInterceptor,
                           grpc.aio.UnaryUnaryClientInterceptor, ):

    async def intercept_service(self,
                                continuation: Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]],
                                caller: grpc.HandlerCallDetails) -> grpc.RpcMethodHandler:
        self.server_context(caller)
        return await continuation(caller)

    async def intercept_stream_stream(self, continuation: Callable[
        [ClientCallDetails, RequestType], StreamStreamCall
    ], client_call_details: ClientCallDetails, request_iterator: RequestIterableType) -> Union[
        ResponseIterableType, StreamStreamCall]:
        return continuation(self.client_context(client_call_details), request_iterator)

    async def intercept_stream_unary(self, continuation: Callable[
        [ClientCallDetails, RequestType], StreamUnaryCall
    ], client_call_details: ClientCallDetails, request_iterator: RequestIterableType) -> StreamUnaryCall:
        return await continuation(self.client_context(client_call_details), request_iterator)

    async def intercept_unary_stream(self, continuation: Callable[
        [ClientCallDetails, RequestType], UnaryStreamCall
    ], client_call_details: ClientCallDetails, request: RequestType) -> Union[ResponseIterableType, UnaryStreamCall]:
        return continuation(self.client_context(client_call_details), request)

    async def intercept_unary_unary(self, continuation: Callable[
        [ClientCallDetails, RequestType], UnaryUnaryCall
    ], client_call_details: ClientCallDetails, request: RequestType) -> Union[UnaryUnaryCall, ResponseType]:
        return await continuation(self.client_context(client_call_details), request)
