import logging
import pickle
import threading
from concurrent import futures
from queue import Empty as EmptyError
from queue import Queue

import grpc
import xarray as xr
from _collections_abc import AsyncIterator, Iterator
from google.protobuf.timestamp_pb2 import Timestamp

from ..configuration import Config, ServerConfig
from .acquisition import EurothermIO, TData
from .proto import service_pb2, service_pb2_grpc

_logger = logging.getLogger(__name__)


class EurothermServicer(service_pb2_grpc.EurothermServicer):

    def __init__(self, cfg: Config) -> None:
        super().__init__()
        self.stop_event = threading.Event()
        self.io = EurothermIO(cfg.devices)

    def StopServer(
        self,
        request: service_pb2.StopRequest,
        context: grpc.ServicerContext,
    ) -> service_pb2.Empty:
        _logger.info('[Request] StopServer')
        self.io.complete()  # stop data acquisition
        self.stop_event.set()
        return service_pb2.Empty()

    def ServerHealthCheck(
        self,
        request: service_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> service_pb2.Empty:
        _logger.info('[Request] ServerHealthCheck')
        return service_pb2.Empty()

    def StreamProcessValues(
        self,
        request: service_pb2.StreamProcessValuesRequest,
        context: grpc.ServicerContext,
    ) -> Iterator[service_pb2.ProcessValues] | AsyncIterator[service_pb2.ProcessValues]:
        _logger.info('[Request] StreamTemperatures')

        # start acquisition thread if necessary
        self.io.start()

        # place streamed values into a synchronized queue
        # (this works because the observable emits all values
        # on a different ThreadPool thread)
        q = Queue[TData]()
        finished = threading.Event()

        def errored(e: Exception):
            _logger.exception('Error on observable.', exc_info=e)
            finished.set()

        def log(x):
            _logger.info(x)
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
            _logger.info('Starting stream...')
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
            _logger.info('...stream stopped.')


class EurothermClient:

    def __init__(self, channel: grpc.Channel) -> None:
        self._client = service_pb2_grpc.EurothermStub(channel)

    def stop_server(self):
        self._client.StopServer(service_pb2.StopRequest())

    def is_alive(self):
        self._client.ServerHealthCheck(service_pb2.Empty())

    def stream_process_values(self):
        request = service_pb2.StreamProcessValuesRequest()
        for response in self._client.StreamProcessValues(request):
            yield TData.from_grpc_response(response)


def is_alive(cfg: Config | ServerConfig):
    _logger.info('Checking server health.')
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

    _logger.info(f'Starting TCLogger server at {server_address}')
    server.start()

    def wait_for_termination():
        _logger.info('Waiting for server to terminate...')
        servicer.stop_event.wait()

        _logger.info(f'Stopping server at {server_address}')
        token = server.stop(30.0)
        token.wait(30.0)

        if not token.is_set():
            _logger.error(f'Server did not terminate')
        else:
            _logger.info(f'Server stopped')

    return executor.submit(wait_for_termination)


def connect(cfg: Config | ServerConfig):
    if isinstance(cfg, Config):
        cfg = cfg.server
    server_address = f'{cfg.ip}:{cfg.port}'

    _logger.info(f'Connecting client to server at {server_address}')
    channel = grpc.insecure_channel(server_address)

    return EurothermClient(channel)
