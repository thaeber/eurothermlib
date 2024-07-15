# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from . import service_pb2 as service__pb2

GRPC_GENERATED_VERSION = '1.64.1'
GRPC_VERSION = grpc.__version__
EXPECTED_ERROR_RELEASE = '1.65.0'
SCHEDULED_RELEASE_DATE = 'June 25, 2024'
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    warnings.warn(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in service_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
        + f' This warning will become an error in {EXPECTED_ERROR_RELEASE},'
        + f' scheduled for release on {SCHEDULED_RELEASE_DATE}.',
        RuntimeWarning
    )


class EurothermStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.StopServer = channel.unary_unary(
                '/Eurotherm/StopServer',
                request_serializer=service__pb2.StopRequest.SerializeToString,
                response_deserializer=service__pb2.Empty.FromString,
                _registered_method=True)
        self.ServerHealthCheck = channel.unary_unary(
                '/Eurotherm/ServerHealthCheck',
                request_serializer=service__pb2.Empty.SerializeToString,
                response_deserializer=service__pb2.Empty.FromString,
                _registered_method=True)
        self.StreamProcessValues = channel.unary_stream(
                '/Eurotherm/StreamProcessValues',
                request_serializer=service__pb2.StreamProcessValuesRequest.SerializeToString,
                response_deserializer=service__pb2.ProcessValues.FromString,
                _registered_method=True)
        self.GetProcessValues = channel.unary_unary(
                '/Eurotherm/GetProcessValues',
                request_serializer=service__pb2.GetProcessValuesRequest.SerializeToString,
                response_deserializer=service__pb2.ProcessValues.FromString,
                _registered_method=True)
        self.ToggleRemoteSetpoint = channel.unary_unary(
                '/Eurotherm/ToggleRemoteSetpoint',
                request_serializer=service__pb2.ToggleRemoteSetpointRequest.SerializeToString,
                response_deserializer=service__pb2.Empty.FromString,
                _registered_method=True)
        self.SetRemoteSetpoint = channel.unary_unary(
                '/Eurotherm/SetRemoteSetpoint',
                request_serializer=service__pb2.SetRemoteSetpointRequest.SerializeToString,
                response_deserializer=service__pb2.Empty.FromString,
                _registered_method=True)
        self.AcknowledgeAllAlarms = channel.unary_unary(
                '/Eurotherm/AcknowledgeAllAlarms',
                request_serializer=service__pb2.AcknowlegdeAllAlarmsRequest.SerializeToString,
                response_deserializer=service__pb2.Empty.FromString,
                _registered_method=True)


class EurothermServicer(object):
    """Missing associated documentation comment in .proto file."""

    def StopServer(self, request, context):
        """Terminate/stop server.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ServerHealthCheck(self, request, context):
        """Does nothing. Used to check sever health.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StreamProcessValues(self, request, context):
        """stream process values
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetProcessValues(self, request, context):
        """current process values
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ToggleRemoteSetpoint(self, request, context):
        """enable/disable remote setpoint
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetRemoteSetpoint(self, request, context):
        """set remote setpoint
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AcknowledgeAllAlarms(self, request, context):
        """acknowledge all alarms
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_EurothermServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'StopServer': grpc.unary_unary_rpc_method_handler(
                    servicer.StopServer,
                    request_deserializer=service__pb2.StopRequest.FromString,
                    response_serializer=service__pb2.Empty.SerializeToString,
            ),
            'ServerHealthCheck': grpc.unary_unary_rpc_method_handler(
                    servicer.ServerHealthCheck,
                    request_deserializer=service__pb2.Empty.FromString,
                    response_serializer=service__pb2.Empty.SerializeToString,
            ),
            'StreamProcessValues': grpc.unary_stream_rpc_method_handler(
                    servicer.StreamProcessValues,
                    request_deserializer=service__pb2.StreamProcessValuesRequest.FromString,
                    response_serializer=service__pb2.ProcessValues.SerializeToString,
            ),
            'GetProcessValues': grpc.unary_unary_rpc_method_handler(
                    servicer.GetProcessValues,
                    request_deserializer=service__pb2.GetProcessValuesRequest.FromString,
                    response_serializer=service__pb2.ProcessValues.SerializeToString,
            ),
            'ToggleRemoteSetpoint': grpc.unary_unary_rpc_method_handler(
                    servicer.ToggleRemoteSetpoint,
                    request_deserializer=service__pb2.ToggleRemoteSetpointRequest.FromString,
                    response_serializer=service__pb2.Empty.SerializeToString,
            ),
            'SetRemoteSetpoint': grpc.unary_unary_rpc_method_handler(
                    servicer.SetRemoteSetpoint,
                    request_deserializer=service__pb2.SetRemoteSetpointRequest.FromString,
                    response_serializer=service__pb2.Empty.SerializeToString,
            ),
            'AcknowledgeAllAlarms': grpc.unary_unary_rpc_method_handler(
                    servicer.AcknowledgeAllAlarms,
                    request_deserializer=service__pb2.AcknowlegdeAllAlarmsRequest.FromString,
                    response_serializer=service__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Eurotherm', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('Eurotherm', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Eurotherm(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def StopServer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Eurotherm/StopServer',
            service__pb2.StopRequest.SerializeToString,
            service__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ServerHealthCheck(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Eurotherm/ServerHealthCheck',
            service__pb2.Empty.SerializeToString,
            service__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StreamProcessValues(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/Eurotherm/StreamProcessValues',
            service__pb2.StreamProcessValuesRequest.SerializeToString,
            service__pb2.ProcessValues.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetProcessValues(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Eurotherm/GetProcessValues',
            service__pb2.GetProcessValuesRequest.SerializeToString,
            service__pb2.ProcessValues.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ToggleRemoteSetpoint(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Eurotherm/ToggleRemoteSetpoint',
            service__pb2.ToggleRemoteSetpointRequest.SerializeToString,
            service__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SetRemoteSetpoint(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Eurotherm/SetRemoteSetpoint',
            service__pb2.SetRemoteSetpointRequest.SerializeToString,
            service__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AcknowledgeAllAlarms(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Eurotherm/AcknowledgeAllAlarms',
            service__pb2.AcknowlegdeAllAlarmsRequest.SerializeToString,
            service__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
