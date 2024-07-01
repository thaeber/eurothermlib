import pytest

from eurothermlib.configuration import ServerConfig, Config, DeviceConfig
from eurothermlib.server import connect, is_alive, serve


class TestServer:

    # @pytest.mark.skip('Skipped long running server test')
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
