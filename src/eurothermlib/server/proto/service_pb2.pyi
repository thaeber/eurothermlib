"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import abc
import builtins
import collections.abc
import concurrent.futures
import google.protobuf.descriptor
import google.protobuf.message
import google.protobuf.service
import google.protobuf.timestamp_pb2
import typing

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing.final
class Empty(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___Empty = Empty

@typing.final
class StopRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___StopRequest = StopRequest

@typing.final
class StreamProcessValuesRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___StreamProcessValuesRequest = StreamProcessValuesRequest

@typing.final
class ProcessValues(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DEVICENAME_FIELD_NUMBER: builtins.int
    TIMESTAMP_FIELD_NUMBER: builtins.int
    PROCESSVALUE_FIELD_NUMBER: builtins.int
    SETPOINT_FIELD_NUMBER: builtins.int
    WORKINGSETPOINT_FIELD_NUMBER: builtins.int
    WORKINGOUTPUT_FIELD_NUMBER: builtins.int
    STATUS_FIELD_NUMBER: builtins.int
    deviceName: builtins.str
    processValue: builtins.float
    setpoint: builtins.float
    workingSetpoint: builtins.float
    workingOutput: builtins.float
    status: builtins.int
    @property
    def timestamp(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    def __init__(
        self,
        *,
        deviceName: builtins.str = ...,
        timestamp: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        processValue: builtins.float = ...,
        setpoint: builtins.float = ...,
        workingSetpoint: builtins.float = ...,
        workingOutput: builtins.float = ...,
        status: builtins.int = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["timestamp", b"timestamp"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["deviceName", b"deviceName", "processValue", b"processValue", "setpoint", b"setpoint", "status", b"status", "timestamp", b"timestamp", "workingOutput", b"workingOutput", "workingSetpoint", b"workingSetpoint"]) -> None: ...

global___ProcessValues = ProcessValues

class Eurotherm(google.protobuf.service.Service, metaclass=abc.ABCMeta):
    DESCRIPTOR: google.protobuf.descriptor.ServiceDescriptor
    @abc.abstractmethod
    def StopServer(
        inst: Eurotherm,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___StopRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None,
    ) -> concurrent.futures.Future[global___Empty]:
        """Terminate/stop server."""

    @abc.abstractmethod
    def ServerHealthCheck(
        inst: Eurotherm,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___Empty,
        callback: collections.abc.Callable[[global___Empty], None] | None,
    ) -> concurrent.futures.Future[global___Empty]:
        """Does nothing. Used to check sever health."""

    @abc.abstractmethod
    def StreamProcessValues(
        inst: Eurotherm,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___StreamProcessValuesRequest,
        callback: collections.abc.Callable[[global___ProcessValues], None] | None,
    ) -> concurrent.futures.Future[global___ProcessValues]:
        """stream process values"""

class Eurotherm_Stub(Eurotherm):
    def __init__(self, rpc_channel: google.protobuf.service.RpcChannel) -> None: ...
    DESCRIPTOR: google.protobuf.descriptor.ServiceDescriptor
    def StopServer(
        inst: Eurotherm_Stub,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___StopRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None = ...,
    ) -> concurrent.futures.Future[global___Empty]:
        """Terminate/stop server."""

    def ServerHealthCheck(
        inst: Eurotherm_Stub,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___Empty,
        callback: collections.abc.Callable[[global___Empty], None] | None = ...,
    ) -> concurrent.futures.Future[global___Empty]:
        """Does nothing. Used to check sever health."""

    def StreamProcessValues(
        inst: Eurotherm_Stub,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___StreamProcessValuesRequest,
        callback: collections.abc.Callable[[global___ProcessValues], None] | None = ...,
    ) -> concurrent.futures.Future[global___ProcessValues]:
        """stream process values"""
