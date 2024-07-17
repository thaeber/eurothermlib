"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import abc
import collections.abc
import grpc
import grpc.aio
from . import service_pb2
import typing

_T = typing.TypeVar("_T")

class _MaybeAsyncIterator(collections.abc.AsyncIterator[_T], collections.abc.Iterator[_T], metaclass=abc.ABCMeta): ...

class _ServicerContext(grpc.ServicerContext, grpc.aio.ServicerContext):  # type: ignore[misc, type-arg]
    ...

class EurothermStub:
    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    StopServer: grpc.UnaryUnaryMultiCallable[
        service_pb2.StopRequest,
        service_pb2.Empty,
    ]
    """Terminate/stop server."""

    ServerHealthCheck: grpc.UnaryUnaryMultiCallable[
        service_pb2.Empty,
        service_pb2.Empty,
    ]
    """Does nothing. Used to check sever health."""

    StreamProcessValues: grpc.UnaryStreamMultiCallable[
        service_pb2.StreamProcessValuesRequest,
        service_pb2.ProcessValues,
    ]
    """stream process values"""

    GetProcessValues: grpc.UnaryUnaryMultiCallable[
        service_pb2.GetProcessValuesRequest,
        service_pb2.ProcessValues,
    ]
    """current process values"""

    ToggleRemoteSetpoint: grpc.UnaryUnaryMultiCallable[
        service_pb2.ToggleRemoteSetpointRequest,
        service_pb2.Empty,
    ]
    """enable/disable remote setpoint"""

    SetRemoteSetpoint: grpc.UnaryUnaryMultiCallable[
        service_pb2.SetRemoteSetpointRequest,
        service_pb2.Empty,
    ]
    """set remote setpoint"""

    StartTemperatureRamp: grpc.UnaryUnaryMultiCallable[
        service_pb2.StartTemperatureRampRequest,
        service_pb2.Empty,
    ]
    """start remote temperature ramp"""

    ManageTemperatureRamp: grpc.UnaryUnaryMultiCallable[
        service_pb2.ManageTemperatureRampRequest,
        service_pb2.Empty,
    ]
    """hold/resume/stop temperature ramp"""

    AcknowledgeAllAlarms: grpc.UnaryUnaryMultiCallable[
        service_pb2.AcknowlegdeAllAlarmsRequest,
        service_pb2.Empty,
    ]
    """acknowledge all alarms"""

class EurothermAsyncStub:
    StopServer: grpc.aio.UnaryUnaryMultiCallable[
        service_pb2.StopRequest,
        service_pb2.Empty,
    ]
    """Terminate/stop server."""

    ServerHealthCheck: grpc.aio.UnaryUnaryMultiCallable[
        service_pb2.Empty,
        service_pb2.Empty,
    ]
    """Does nothing. Used to check sever health."""

    StreamProcessValues: grpc.aio.UnaryStreamMultiCallable[
        service_pb2.StreamProcessValuesRequest,
        service_pb2.ProcessValues,
    ]
    """stream process values"""

    GetProcessValues: grpc.aio.UnaryUnaryMultiCallable[
        service_pb2.GetProcessValuesRequest,
        service_pb2.ProcessValues,
    ]
    """current process values"""

    ToggleRemoteSetpoint: grpc.aio.UnaryUnaryMultiCallable[
        service_pb2.ToggleRemoteSetpointRequest,
        service_pb2.Empty,
    ]
    """enable/disable remote setpoint"""

    SetRemoteSetpoint: grpc.aio.UnaryUnaryMultiCallable[
        service_pb2.SetRemoteSetpointRequest,
        service_pb2.Empty,
    ]
    """set remote setpoint"""

    StartTemperatureRamp: grpc.aio.UnaryUnaryMultiCallable[
        service_pb2.StartTemperatureRampRequest,
        service_pb2.Empty,
    ]
    """start remote temperature ramp"""

    ManageTemperatureRamp: grpc.aio.UnaryUnaryMultiCallable[
        service_pb2.ManageTemperatureRampRequest,
        service_pb2.Empty,
    ]
    """hold/resume/stop temperature ramp"""

    AcknowledgeAllAlarms: grpc.aio.UnaryUnaryMultiCallable[
        service_pb2.AcknowlegdeAllAlarmsRequest,
        service_pb2.Empty,
    ]
    """acknowledge all alarms"""

class EurothermServicer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def StopServer(
        self,
        request: service_pb2.StopRequest,
        context: _ServicerContext,
    ) -> typing.Union[service_pb2.Empty, collections.abc.Awaitable[service_pb2.Empty]]:
        """Terminate/stop server."""

    @abc.abstractmethod
    def ServerHealthCheck(
        self,
        request: service_pb2.Empty,
        context: _ServicerContext,
    ) -> typing.Union[service_pb2.Empty, collections.abc.Awaitable[service_pb2.Empty]]:
        """Does nothing. Used to check sever health."""

    @abc.abstractmethod
    def StreamProcessValues(
        self,
        request: service_pb2.StreamProcessValuesRequest,
        context: _ServicerContext,
    ) -> typing.Union[collections.abc.Iterator[service_pb2.ProcessValues], collections.abc.AsyncIterator[service_pb2.ProcessValues]]:
        """stream process values"""

    @abc.abstractmethod
    def GetProcessValues(
        self,
        request: service_pb2.GetProcessValuesRequest,
        context: _ServicerContext,
    ) -> typing.Union[service_pb2.ProcessValues, collections.abc.Awaitable[service_pb2.ProcessValues]]:
        """current process values"""

    @abc.abstractmethod
    def ToggleRemoteSetpoint(
        self,
        request: service_pb2.ToggleRemoteSetpointRequest,
        context: _ServicerContext,
    ) -> typing.Union[service_pb2.Empty, collections.abc.Awaitable[service_pb2.Empty]]:
        """enable/disable remote setpoint"""

    @abc.abstractmethod
    def SetRemoteSetpoint(
        self,
        request: service_pb2.SetRemoteSetpointRequest,
        context: _ServicerContext,
    ) -> typing.Union[service_pb2.Empty, collections.abc.Awaitable[service_pb2.Empty]]:
        """set remote setpoint"""

    @abc.abstractmethod
    def StartTemperatureRamp(
        self,
        request: service_pb2.StartTemperatureRampRequest,
        context: _ServicerContext,
    ) -> typing.Union[service_pb2.Empty, collections.abc.Awaitable[service_pb2.Empty]]:
        """start remote temperature ramp"""

    @abc.abstractmethod
    def ManageTemperatureRamp(
        self,
        request: service_pb2.ManageTemperatureRampRequest,
        context: _ServicerContext,
    ) -> typing.Union[service_pb2.Empty, collections.abc.Awaitable[service_pb2.Empty]]:
        """hold/resume/stop temperature ramp"""

    @abc.abstractmethod
    def AcknowledgeAllAlarms(
        self,
        request: service_pb2.AcknowlegdeAllAlarmsRequest,
        context: _ServicerContext,
    ) -> typing.Union[service_pb2.Empty, collections.abc.Awaitable[service_pb2.Empty]]:
        """acknowledge all alarms"""

def add_EurothermServicer_to_server(servicer: EurothermServicer, server: typing.Union[grpc.Server, grpc.aio.Server]) -> None: ...
