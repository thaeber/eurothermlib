from eurothermlib.configuration import ServerConfig


class TestServerConfig:
    def test_create_default_instance(self):
        config = ServerConfig()
        assert str(config.ip) == '127.0.0.1'
        assert config.port == 50061

    def test_create_instance(self):
        config = ServerConfig(ip='127.0.0.1', port=180)  # type: ignore
        assert str(config.ip) == '127.0.0.1'
        assert config.port == 180
