import pytest

from eurothermlib.configuration import ServerConfig
from eurothermlib.server import connect, is_alive, serve


class TestServer:

    @pytest.mark.skip('Skipped long running server test')
    def test_serve(self):
        config = ServerConfig()
        future = serve(config)
        assert future.running()
        assert is_alive(config)

        client = connect(config)
        client.stop_server()
        assert not is_alive(config)
