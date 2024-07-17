"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import abc
import builtins
import collections.abc
import concurrent.futures
import google.protobuf.descriptor
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import google.protobuf.service
import google.protobuf.timestamp_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _TemperatureRampState:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _TemperatureRampStateEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_TemperatureRampState.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    TRS_NORAMP: _TemperatureRampState.ValueType  # 0
    TRS_RAMPING: _TemperatureRampState.ValueType  # 1
    TRS_HOLDING: _TemperatureRampState.ValueType  # 2
    TRS_STOPPED: _TemperatureRampState.ValueType  # 3
    TRS_FINISHED: _TemperatureRampState.ValueType  # 4

class TemperatureRampState(_TemperatureRampState, metaclass=_TemperatureRampStateEnumTypeWrapper): ...

TRS_NORAMP: TemperatureRampState.ValueType  # 0
TRS_RAMPING: TemperatureRampState.ValueType  # 1
TRS_HOLDING: TemperatureRampState.ValueType  # 2
TRS_STOPPED: TemperatureRampState.ValueType  # 3
TRS_FINISHED: TemperatureRampState.ValueType  # 4
global___TemperatureRampState = TemperatureRampState

class _RemoteSetpointState:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _RemoteSetpointStateEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_RemoteSetpointState.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    DISABLED: _RemoteSetpointState.ValueType  # 0
    ENABLED: _RemoteSetpointState.ValueType  # 1

class RemoteSetpointState(_RemoteSetpointState, metaclass=_RemoteSetpointStateEnumTypeWrapper): ...

DISABLED: RemoteSetpointState.ValueType  # 0
ENABLED: RemoteSetpointState.ValueType  # 1
global___RemoteSetpointState = RemoteSetpointState

class _TemperatureRampAction:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _TemperatureRampActionEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_TemperatureRampAction.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    HOLD: _TemperatureRampAction.ValueType  # 0
    RESUME: _TemperatureRampAction.ValueType  # 1
    STOP: _TemperatureRampAction.ValueType  # 2

class TemperatureRampAction(_TemperatureRampAction, metaclass=_TemperatureRampActionEnumTypeWrapper): ...

HOLD: TemperatureRampAction.ValueType  # 0
RESUME: TemperatureRampAction.ValueType  # 1
STOP: TemperatureRampAction.ValueType  # 2
global___TemperatureRampAction = TemperatureRampAction

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
class GetProcessValuesRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DEVICENAME_FIELD_NUMBER: builtins.int
    deviceName: builtins.str
    def __init__(
        self,
        *,
        deviceName: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["deviceName", b"deviceName"]) -> None: ...

global___GetProcessValuesRequest = GetProcessValuesRequest

@typing.final
class ProcessValues(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DEVICENAME_FIELD_NUMBER: builtins.int
    TIMESTAMP_FIELD_NUMBER: builtins.int
    STATUS_FIELD_NUMBER: builtins.int
    PROCESSVALUE_FIELD_NUMBER: builtins.int
    SETPOINT_FIELD_NUMBER: builtins.int
    WORKINGSETPOINT_FIELD_NUMBER: builtins.int
    REMOTESETPOINT_FIELD_NUMBER: builtins.int
    WORKINGOUTPUT_FIELD_NUMBER: builtins.int
    RAMPSTATUS_FIELD_NUMBER: builtins.int
    deviceName: builtins.str
    status: builtins.int
    processValue: builtins.float
    setpoint: builtins.float
    workingSetpoint: builtins.float
    remoteSetpoint: builtins.float
    workingOutput: builtins.float
    rampStatus: global___TemperatureRampState.ValueType
    @property
    def timestamp(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    def __init__(
        self,
        *,
        deviceName: builtins.str = ...,
        timestamp: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        status: builtins.int = ...,
        processValue: builtins.float = ...,
        setpoint: builtins.float = ...,
        workingSetpoint: builtins.float = ...,
        remoteSetpoint: builtins.float = ...,
        workingOutput: builtins.float = ...,
        rampStatus: global___TemperatureRampState.ValueType = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["timestamp", b"timestamp"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["deviceName", b"deviceName", "processValue", b"processValue", "rampStatus", b"rampStatus", "remoteSetpoint", b"remoteSetpoint", "setpoint", b"setpoint", "status", b"status", "timestamp", b"timestamp", "workingOutput", b"workingOutput", "workingSetpoint", b"workingSetpoint"]) -> None: ...

global___ProcessValues = ProcessValues

@typing.final
class ToggleRemoteSetpointRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DEVICENAME_FIELD_NUMBER: builtins.int
    STATE_FIELD_NUMBER: builtins.int
    deviceName: builtins.str
    state: global___RemoteSetpointState.ValueType
    def __init__(
        self,
        *,
        deviceName: builtins.str = ...,
        state: global___RemoteSetpointState.ValueType = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["deviceName", b"deviceName", "state", b"state"]) -> None: ...

global___ToggleRemoteSetpointRequest = ToggleRemoteSetpointRequest

@typing.final
class SetRemoteSetpointRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DEVICENAME_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    deviceName: builtins.str
    value: builtins.float
    """temperature [K]"""
    def __init__(
        self,
        *,
        deviceName: builtins.str = ...,
        value: builtins.float = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["deviceName", b"deviceName", "value", b"value"]) -> None: ...

global___SetRemoteSetpointRequest = SetRemoteSetpointRequest

@typing.final
class StartTemperatureRampRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DEVICENAME_FIELD_NUMBER: builtins.int
    TARGET_FIELD_NUMBER: builtins.int
    RATE_FIELD_NUMBER: builtins.int
    deviceName: builtins.str
    target: builtins.float
    """target temperature [K]"""
    rate: builtins.float
    """rate of change [K/min]"""
    def __init__(
        self,
        *,
        deviceName: builtins.str = ...,
        target: builtins.float = ...,
        rate: builtins.float = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["deviceName", b"deviceName", "rate", b"rate", "target", b"target"]) -> None: ...

global___StartTemperatureRampRequest = StartTemperatureRampRequest

@typing.final
class ManageTemperatureRampRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DEVICENAME_FIELD_NUMBER: builtins.int
    ACTION_FIELD_NUMBER: builtins.int
    deviceName: builtins.str
    action: global___TemperatureRampAction.ValueType
    def __init__(
        self,
        *,
        deviceName: builtins.str = ...,
        action: global___TemperatureRampAction.ValueType = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["action", b"action", "deviceName", b"deviceName"]) -> None: ...

global___ManageTemperatureRampRequest = ManageTemperatureRampRequest

@typing.final
class AcknowlegdeAllAlarmsRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DEVICENAME_FIELD_NUMBER: builtins.int
    deviceName: builtins.str
    def __init__(
        self,
        *,
        deviceName: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["deviceName", b"deviceName"]) -> None: ...

global___AcknowlegdeAllAlarmsRequest = AcknowlegdeAllAlarmsRequest

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

    @abc.abstractmethod
    def GetProcessValues(
        inst: Eurotherm,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___GetProcessValuesRequest,
        callback: collections.abc.Callable[[global___ProcessValues], None] | None,
    ) -> concurrent.futures.Future[global___ProcessValues]:
        """current process values"""

    @abc.abstractmethod
    def ToggleRemoteSetpoint(
        inst: Eurotherm,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___ToggleRemoteSetpointRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None,
    ) -> concurrent.futures.Future[global___Empty]:
        """enable/disable remote setpoint"""

    @abc.abstractmethod
    def SetRemoteSetpoint(
        inst: Eurotherm,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___SetRemoteSetpointRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None,
    ) -> concurrent.futures.Future[global___Empty]:
        """set remote setpoint"""

    @abc.abstractmethod
    def StartTemperatureRamp(
        inst: Eurotherm,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___StartTemperatureRampRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None,
    ) -> concurrent.futures.Future[global___Empty]:
        """start remote temperature ramp"""

    @abc.abstractmethod
    def ManageTemperatureRamp(
        inst: Eurotherm,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___ManageTemperatureRampRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None,
    ) -> concurrent.futures.Future[global___Empty]:
        """hold/resume/stop temperature ramp"""

    @abc.abstractmethod
    def AcknowledgeAllAlarms(
        inst: Eurotherm,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___AcknowlegdeAllAlarmsRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None,
    ) -> concurrent.futures.Future[global___Empty]:
        """acknowledge all alarms"""

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

    def GetProcessValues(
        inst: Eurotherm_Stub,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___GetProcessValuesRequest,
        callback: collections.abc.Callable[[global___ProcessValues], None] | None = ...,
    ) -> concurrent.futures.Future[global___ProcessValues]:
        """current process values"""

    def ToggleRemoteSetpoint(
        inst: Eurotherm_Stub,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___ToggleRemoteSetpointRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None = ...,
    ) -> concurrent.futures.Future[global___Empty]:
        """enable/disable remote setpoint"""

    def SetRemoteSetpoint(
        inst: Eurotherm_Stub,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___SetRemoteSetpointRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None = ...,
    ) -> concurrent.futures.Future[global___Empty]:
        """set remote setpoint"""

    def StartTemperatureRamp(
        inst: Eurotherm_Stub,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___StartTemperatureRampRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None = ...,
    ) -> concurrent.futures.Future[global___Empty]:
        """start remote temperature ramp"""

    def ManageTemperatureRamp(
        inst: Eurotherm_Stub,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___ManageTemperatureRampRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None = ...,
    ) -> concurrent.futures.Future[global___Empty]:
        """hold/resume/stop temperature ramp"""

    def AcknowledgeAllAlarms(
        inst: Eurotherm_Stub,  # pyright: ignore[reportSelfClsParameterName]
        rpc_controller: google.protobuf.service.RpcController,
        request: global___AcknowlegdeAllAlarmsRequest,
        callback: collections.abc.Callable[[global___Empty], None] | None = ...,
    ) -> concurrent.futures.Future[global___Empty]:
        """acknowledge all alarms"""
