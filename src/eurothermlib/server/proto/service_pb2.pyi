"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import abc
import collections.abc
import concurrent.futures
import google.protobuf.descriptor
import google.protobuf.message
import google.protobuf.service
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
