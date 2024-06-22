import logging
import threading
from concurrent import futures
from typing import TypeVar

import grpc

from ..configuration import ServerConfig
from .proto import service_pb2, service_pb2_grpc

_logger = logging.getLogger(__name__)


class EurothermServicer(service_pb2_grpc.EurothermServicer):

    def __init__(self) -> None:
        super().__init__()
        self.stop_event = threading.Event()

    def StopServer(
        self,
        request: service_pb2.StopRequest,
        context: grpc.ServicerContext,
    ) -> service_pb2.Empty:
        _logger.info('[Request] StopServer')
        # self.io.complete()  # stop data acquisition
        self.stop_event.set()
        return service_pb2.Empty()

    def ServerHealthCheck(
        self,
        request: service_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> service_pb2.Empty:
        _logger.info('[Request] ServerHealthCheck')
        return service_pb2.Empty()


class EurothermClient:

    def __init__(self, channel: grpc.Channel) -> None:
        self._client = service_pb2_grpc.EurothermStub(channel)

    def stop_server(self):
        self._client.StopServer(service_pb2.StopRequest())

    def is_alive(self):
        self._client.ServerHealthCheck(service_pb2.Empty())


def is_alive(cfg: ServerConfig):
    _logger.info('Checking server health.')
    client = connect(cfg)
    try:
        client.is_alive()
        return True
    except grpc.RpcError:
        return False


def serve(cfg: ServerConfig):
    executor = futures.ThreadPoolExecutor()
    server = grpc.server(executor)
    servicer = EurothermServicer()
    service_pb2_grpc.add_EurothermServicer_to_server(servicer, server)

    server_address = f'{cfg.ip}:{cfg.port}'
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


def connect(cfg: ServerConfig):
    server_address = f'{cfg.ip}:{cfg.port}'

    _logger.info(f'Connecting client to server at {server_address}')
    channel = grpc.insecure_channel(server_address)

    return EurothermClient(channel)
