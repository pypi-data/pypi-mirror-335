#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from mesh.asm import *
from mesh.boost import *
from mesh.cause import *
from mesh.codec import *
from mesh.context import *
from mesh.environ import *
from mesh.log import *
from mesh.macro import *
from mesh.mpc import *
from mesh.prsim import *

__all__ = (
    "mpi",
    "mps",
    "index",
    "spi",
    "binding",
    "Codeable",
    "Cause",
    "Inspector",
    "Types",
    "ServiceLoader",
    ##
    "URN",
    "URNFlag",
    "Consumer",
    "Filter",
    "Invocation",
    "Provider",
    "ServiceProxy",
    "MeshKey",
    "Mesh",
    # cause
    "MeshException",
    "CompatibleException",
    "NotFoundException",
    "ValidationException",
    "Codec",
    # prsim
    "Builtin",
    "Cache",
    "Cluster",
    "Commercialize",
    "RunMode",
    "Key",
    "Metadata",
    "Queue",
    "Context",
    "Cryptor",
    "DataHouse",
    "Dispatcher",
    "Endpoint",
    "EndpointSticker",
    "Evaluator",
    "Graphics",
    "Hodor",
    "IOStream",
    "KV",
    "Licenser",
    "Locker",
    "Network",
    "Publisher",
    "Registry",
    "Routable",
    "RuntimeHook",
    "Scheduler",
    "Sequence",
    "Subscriber",
    "Tokenizer",
    "Transport",
    "Session",
    #
    "Runtime",
    "MethodProxy",
    "Metadata",
)

__mooter__ = Mooter()


def init():
    asm.init()


async def start():
    await __mooter__.start()


async def refresh():
    await __mooter__.refresh()


async def stop():
    await __mooter__.stop()


async def wait():
    """
    Use signal handler to throw exception which can be caught to allow graceful exit.
    """
    await __mooter__.wait()
