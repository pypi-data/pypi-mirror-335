#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from asyncio import CancelledError
from concurrent.futures import Future
from typing import Iterator, Union, Any

import grpc

import mesh.tool as tool
from mesh.cause import TimeoutException, MeshException, NotFoundException, MeshCode
from mesh.context import Mesh
from mesh.environ import System
from mesh.grpx.bfia import BfiaBinding, bfia_consume
from mesh.grpx.channels import GrpcChannels
from mesh.grpx.interceptor import MeshInterceptor
from mesh.kinds import Reference
from mesh.macro import spi
from mesh.mpc.consumer import Consumer
from mesh.mpc.invoker import Execution
from mesh.mpc.urn import URN


@spi("grpc")
class GrpcConsumer(Consumer):

    def __init__(self):
        self.channel = GrpcChannels()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Close """
        self.channel.__exit__(exc_type, exc_val, exc_tb)

    def start(self):
        """ Do not need to implement """
        pass

    async def consume(self, address: str, urn: URN, execution: Execution[Reference], inbound: bytes,
                      args: Any) -> bytes:
        """
        request_iterator=iterator,
        timeout=None,
        metadata=None,
        credentials=None,
        wait_for_ready=None,
        compression=None
        :param address:
        :param urn:
        :param execution:
        :param inbound:
        :param args:
        :return:
        """
        binding = BfiaBinding(urn.string(), args)
        if "" != binding.path:
            return await bfia_consume(address, binding, execution, inbound, self.channel)

        ct = Mesh.context().get_attribute(Mesh.TIMEOUT)
        timeout = (ct if ct else execution.schema().timeout) / 1000
        # Interceptor ahead because asyncio interceptor has no fixed order.
        metadata = MeshInterceptor.context_metadata()
        try:
            return await self.channel.unary(address, inbound, timeout, metadata)
        except grpc.FutureTimeoutError:
            raise TimeoutException(f'Invoke {execution.schema().urn} timeout with {timeout * 1000}ms')
        except grpc.FutureCancelledError:
            raise MeshException(MeshCode.SYSTEM_ERROR.get_code(), f'Invoke {execution.schema().urn} canceled')
        except CancelledError as e:
            raise e
        except grpc.RpcError as e:
            if isinstance(e, grpc.Call):
                if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    raise TimeoutException(f'Invoke {urn.name} timeout with {execution.schema().timeout}ms')
                if e.code() == grpc.StatusCode.UNKNOWN:
                    raise NotFoundException(f'Service {urn.name} not found')
                raise MeshException(MeshCode.SYSTEM_ERROR.get_code(), f'Invoke {urn.name} {e.code()} {e.details()}')
            raise e

    @staticmethod
    def resolve(address: str):
        hosts = tool.split(address, ":")
        if hosts.__len__() < 2:
            return f'{hosts[0]}:{System.environ().get_default_mesh_port()}'
        return address

    def reset_if_unconnected(self, channel: GrpcChannels):
        def x(e: BaseException):
            pass

        return x


class AsyncInvokeObserver(Future, grpc.Call):

    def __init__(self, rendezvous: Union[grpc.Future, grpc.Call]):
        super().__init__()
        self.rendezvous = rendezvous

    def initial_metadata(self):
        self.rendezvous.initial_metadata()

    def trailing_metadata(self):
        return self.rendezvous.trailing_metadata()

    def code(self):
        return self.rendezvous.code()

    def details(self):
        return self.rendezvous.details()

    def is_active(self):
        return self.rendezvous.is_active()

    def time_remaining(self):
        return self.rendezvous.time_remaining()

    def add_callback(self, callback):
        return self.rendezvous.add_callback(callback)


class IterableBuffer(Iterator):

    def __init__(self, buffer: bytes):
        self.buffer = list()
        self.buffer.append(buffer)

    def __next__(self) -> bytes:
        if self.buffer:
            return self.buffer.pop()
        raise StopIteration()


class GrpcFuture(grpc.Future):

    def __init__(self, future: grpc.Future, hooks: Any) -> None:
        self.future = future
        self.hooks = hooks

    def cancel(self, msg: Any = ...) -> bool:
        return self.future.cancel()

    def cancelled(self):
        return self.future.cancelled()

    def running(self):
        return self.future.running()

    def done(self):
        return self.future.done()

    def result(self, timeout=None):
        return self.future.result(timeout)

    def exception(self, timeout=None):
        return self.future.exception(timeout)

    def traceback(self, timeout=None):
        return self.future.traceback(timeout)

    def add_done_callback(self, fn):
        return self.future.add_done_callback(fn)
