import pytest
from toolz.curried import pipe, take

from eurothermlib.configuration import Config, DeviceConfig, ServerConfig
from eurothermlib.server import connect, is_alive, serve


class TestServer:
    @pytest.mark.slow
    def test_serve(self):
        config = Config(
            server=ServerConfig(),
            devices=[
                DeviceConfig(name='device1', sampling_rate='5Hz'),  # type: ignore
                DeviceConfig(name='device2', sampling_rate='2Hz'),  # type: ignore
            ],
        )

        future = serve(config)
        assert future.running()
        assert is_alive(config)

        client = connect(config)
        client.stop_server()
        assert not is_alive(config)


class TestClient:
    @pytest.mark.slow
    def test_stream_process_values(self):
        config = Config(
            server=ServerConfig(),
            devices=[
                DeviceConfig(name='device1', sampling_rate='5Hz'),  # type: ignore
                DeviceConfig(name='device2', sampling_rate='2Hz'),  # type: ignore
            ],
        )

        future = serve(config)
        assert future.running()
        client = connect(config)

        try:
            data = pipe(
                client.stream_process_values(),
                take(10),
                list,
            )
            assert isinstance(data, list)
            assert len(data) == 10

        finally:
            client.stop_server()
