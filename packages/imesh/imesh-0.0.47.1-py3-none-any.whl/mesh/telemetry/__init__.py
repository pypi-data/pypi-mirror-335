#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

import random

from opentelemetry import trace
from opentelemetry.trace import Tracer, NonRecordingSpan
from opentelemetry.trace.span import Span, SpanContext, TraceFlags, INVALID_SPAN

from mesh.environ import System
from mesh.telemetry.telemetry import MeshTelemetry
from mesh.telemetry.telemetry_filter import TelemetryConsumerFilter, TelemetryProviderFilter

mot = MeshTelemetry()

__all__ = (
    "TelemetryConsumerFilter",
    "TelemetryProviderFilter"
)


def init():
    """ init function """
    pass


def provider_tracer(tracer_name: str = '', print_std: bool = False) -> "Tracer":
    """
    :param tracer_name: app name may be better
    :param print_std: True: print metrics data on stdout; False: ignore
    :return: Tracer, used as below,
    for example:
    with tracer.start_as_current_span("asm.init"):
        pass
    """
    __tracer__ = mot.get_tracer(service_name=System.environ().get_mesh_name(), enable_std=print_std)
    if __tracer__:
        if tracer_name != '':
            return __tracer__.get_tracer(tracer_name)
        else:
            return __tracer__.get_tracer(System.environ().get_mesh_name())
    else:
        print('open telemetry not active!')
        # raise Exception('open telemetry not active!')


def get_current_span() -> Span:
    return trace.get_current_span()


tracer = provider_tracer(tracer_name=System.environ().get_mesh_name(),
                         print_std=System.environ().enable_telemetry_std())


def if_rebuild_span() -> bool:
    # tracer may be not active
    if not tracer:
        return False
    return True


def reset_ctx(trace_id: int, span_id: int):
    """
    force set span context with input trace_id and span_id
    trace_id and span_id should be valid, or will be reset randomly
    :param trace_id:
    :param span_id:
    :return:
    """
    trace_id = _choose_trace_id(trace_id)
    span_id = _choose_span_id(span_id)
    span_context = SpanContext(trace_id=trace_id,
                               span_id=span_id,
                               is_remote=True,
                               trace_flags=TraceFlags.SAMPLED)
    # propagate context
    trace.set_span_in_context(NonRecordingSpan(span_context))


def build_via_remote(attachments: dict, name: str):
    """
    enable only for if_rebuild_span return True
    :param name:
    :param attachments: mesh context
    :return: telemetry Span
    """
    ctx = None
    trace_id = 0
    if 'mesh-telemetry-trace-id' in attachments:
        trace_id = int(attachments['mesh-telemetry-trace-id'], 16)
    if trace.get_current_span() == INVALID_SPAN or \
            (trace_id != 0 and get_current_span().get_span_context().trace_id != trace_id):
        span_context = SpanContext(trace_id=_choose_trace_id(trace_id),
                                   span_id=_choose_span_id(),
                                   is_remote=True,
                                   trace_flags=TraceFlags.SAMPLED)
        ctx = trace.set_span_in_context(NonRecordingSpan(span_context))
    return tracer.start_as_current_span(name=name, context=ctx)


def _choose_trace_id(trace_id: int) -> int:
    """
    trace_id should generate in open telemetry trace_id style
    :param trace_id:
    :return:
    """
    if trace_id == 0:
        return random.getrandbits(128)
    return trace_id


def _choose_span_id(span_id: int = 0) -> int:
    """
    span_id should generate in open telemetry span_id style
    :param span_id:
    :return:
    """
    if span_id == 0:
        return random.getrandbits(64)
    return span_id
