import logging
import threading
from concurrent import futures
from enum import IntEnum
from queue import Empty as EmptyError
from queue import Queue
from typing import Optional

import grpc
import reactivex.operators as op
from _collections_abc import AsyncIterator, Awaitable, Iterator

from eurothermlib.controllers.controller import RemoteSetpointState
from eurothermlib.utils import TemperatureQ

from ..configuration import Config, ServerConfig
from .acquisition import EurothermIO, TData
from .proto import service_pb2, service_pb2_grpc

logger = logging.getLogger(__name__)


class EurothermServicer(service_pb2_grpc.EurothermServicer):
    def __init__(self, cfg: Config) -> None:
        super().__init__()
        self.stop_event = threading.Event()
        self.io = EurothermIO(cfg.devices)

    def StopServer(
        self,
        request: service_pb2.StopRequest,
        context: grpc.ServicerContext,
    ):
        logger.info('[Request] StopServer')
        self.io.complete()  # stop data acquisition
        self.stop_event.set()
        return service_pb2.Empty()

    def ServerHealthCheck(
        self,
        request: service_pb2.Empty,
        context: grpc.ServicerContext,
    ):
        logger.info('[Request] ServerHealthCheck')
        return service_pb2.Empty()

    def StreamProcessValues(
        self,
        request: service_pb2.StreamProcessValuesRequest,
        context: grpc.ServicerContext,
    ):
        logger.info('[Request] StreamTemperatures')

        # start acquisition thread if necessary
        self.io.start()

        # place streamed values into a synchronized queue
        # (this works because the observable emits all values
        # on a different ThreadPool thread)
        q = Queue[TData]()
        finished = threading.Event()

        def errored(e: Exception):
            logger.exception('Error on observable.', exc_info=e)
            finished.set()

        def log(x):
            logger.info(x)
            return x

        observable = self.io.observable

        subscription = observable.subscribe(
            q.put,
            on_completed=finished.set,
            on_error=errored,
        )

        def cancel():
            return finished.is_set() or self.stop_event.is_set()

        try:
            logger.info('Starting stream...')
            while not cancel():
                try:
                    da = q.get(timeout=5)
                    # _logger.info(f'Yielding at {timestamp}')
                    yield da.to_grpc_response()
                except EmptyError:
                    pass
        finally:
            # dispose subscription once iteration completes or terminates
            subscription.dispose()
            logger.info('...stream stopped.')

    def GetProcessValues(
        self,
        request: service_pb2.GetProcessValuesRequest,
        context: grpc.ServicerContext,
    ):
        logger.info(
            f'[Request] [{repr(request.deviceName)}] Get current process values & instrument status'
        )

        # start acquisition thread if necessary
        self.io.start()

        observable = self.io.observable

        values: TData = observable.pipe(
            op.filter(lambda x: x.deviceName == request.deviceName),
            op.take(1),
        ).run()

        return values.to_grpc_response()

    def ToggleRemoteSetpoint(
        self,
        request: service_pb2.ToggleRemoteSetpointRequest,
        context: grpc.ServicerContext,
    ):
        # start acquisition thread if necessary
        self.io.start()

        match request.state:
            case service_pb2.RemoteSetpointState.ENABLED:
                state = RemoteSetpointState.ENABLE
            case service_pb2.RemoteSetpointState.DISABLED:
                state = RemoteSetpointState.DISBALE

        logger.info(
            f'[Request] [{repr(request.deviceName)}] Setting local remote setpoint selector to: {repr(state)}'
        )
        self.io.toggle_remote_setpoint(request.deviceName, state)

        return service_pb2.Empty()

    def SetRemoteSetpoint(
        self,
        request: service_pb2.SetRemoteSetpointRequest,
        context: grpc.ServicerContext,
    ):
        # start acquisition thread if necessary
        self.io.start()

        value = TemperatureQ(request.value, 'K')
        logger.info(
            f'[Request] [{repr(request.deviceName)}] Set remote setpoint to: {value:.2f~P}'
        )
        self.io.set_remote_setpoint(request.deviceName, value)

        return service_pb2.Empty()

    def AcknowledgeAllAlarms(
        self,
        request: service_pb2.AcknowlegdeAllAlarmsRequest,
        context: grpc.ServicerContext,
    ):
        # start acquisition thread if necessary
        self.io.start()

        logger.info(f'[Request] [{repr(request.deviceName)}] Acknowledge all alarms')
        self.io.acknowledge_all_alarms(request.deviceName)
        return service_pb2.Empty()


class EurothermClient:
    def __init__(self, channel: grpc.Channel, cfg: ServerConfig) -> None:
        self._client = service_pb2_grpc.EurothermStub(channel)
        self._cfg = cfg

    @property
    def timeout(self):
        return self._cfg.timeout.m_as('s')

    def stop_server(self):
        self._client.StopServer(service_pb2.StopRequest())

    def is_alive(self):
        self._client.ServerHealthCheck(service_pb2.Empty(), timeout=self.timeout)

    def stream_process_values(self):
        request = service_pb2.StreamProcessValuesRequest()
        for response in self._client.StreamProcessValues(request):
            yield TData.from_grpc_response(response)

    def current_process_values(self, device: str):
        logger.info(f'[{repr(device)}] Reading process values')
        request = service_pb2.GetProcessValuesRequest(deviceName=device)
        response = self._client.GetProcessValues(request, timeout=self.timeout)
        return TData.from_grpc_response(response)

    def toggle_remote_setpoint(
        self,
        device: str,
        state: RemoteSetpointState,
    ):
        match state:
            case RemoteSetpointState.ENABLE:
                _state = service_pb2.RemoteSetpointState.ENABLED
                logger.info(f'[{repr(device)}] Enabling remote setpoint')
            case RemoteSetpointState.DISBALE:
                _state = service_pb2.RemoteSetpointState.DISABLED
                logger.info(f'[{repr(device)}] Disabling remote setpoint')
                logger.warn(f'[{repr(device)}] Falling back to internal setpoint')
            case _:
                logger.error(f'Unknown remote setpoint state: {state}')
        request = service_pb2.ToggleRemoteSetpointRequest(
            deviceName=device,
            state=_state,
        )
        self._client.ToggleRemoteSetpoint(request, timeout=self.timeout)

    def set_remote_setpoint(self, device: str, value: TemperatureQ):
        logger.info(f'[{repr(device)}] Setting remote setpoint: {value:.2f~P}')
        request = service_pb2.SetRemoteSetpointRequest(
            deviceName=device,
            value=value.m_as('K'),
        )
        self._client.SetRemoteSetpoint(request)

    def acknowledge_all_alarms(self, device: str):
        logger.info(f'[{repr(device)}] Acknowledging all alarms')
        self._client.AcknowledgeAllAlarms(
            service_pb2.AcknowlegdeAllAlarmsRequest(deviceName=device)
        )


def is_alive(cfg: Config | ServerConfig):
    logger.info('Checking server health.')
    if isinstance(cfg, Config):
        cfg = cfg.server
    client = connect(cfg)
    try:
        client.is_alive()
        return True
    except grpc.RpcError:
        return False


def serve(cfg: Config):
    executor = futures.ThreadPoolExecutor()
    server = grpc.server(executor)
    servicer = EurothermServicer(cfg)
    service_pb2_grpc.add_EurothermServicer_to_server(servicer, server)

    server_address = f'{cfg.server.ip}:{cfg.server.port}'
    server.add_insecure_port(server_address)

    logger.info(f'Starting TCLogger server at {server_address}')
    server.start()

    def wait_for_termination():
        logger.info('Waiting for server to terminate...')
        servicer.stop_event.wait()

        logger.info(f'Stopping server at {server_address}')
        token = server.stop(30.0)
        token.wait(30.0)

        if not token.is_set():
            logger.error('Server did not terminate')
        else:
            logger.info('Server stopped')

    return executor.submit(wait_for_termination)


def connect(cfg: Config | ServerConfig):
    if isinstance(cfg, Config):
        cfg = cfg.server
    server_address = f'{cfg.ip}:{cfg.port}'

    logger.info(f'Connecting client to server at {server_address}')
    channel = grpc.insecure_channel(server_address)

    return EurothermClient(channel, cfg)
