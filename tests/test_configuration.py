from eurothermlib.configuration import (
    Config,
    DeviceConfig,
    SerialPortConfig,
    ServerConfig,
)


class TestServerConfig:
    def test_create_default_instance(self):
        config = ServerConfig()
        assert str(config.ip) == '127.0.0.1'
        assert config.port == 50061

    def test_create_instance(self):
        config = ServerConfig(ip='127.0.0.1', port=180)  # type: ignore
        assert str(config.ip) == '127.0.0.1'
        assert config.port == 180


class TestSerialPortConfig:
    def test_create_default_instance(self):
        config = SerialPortConfig()
        assert config.port == 'COM1'
        assert config.baudRate == 19200


class TestDeviceConfig:
    def test_create_default_instance(self):
        config = DeviceConfig()
        assert config.unitAddress == 1
        assert config.sampling_rate == 1.0
        assert config.simulate == True


class TestConfig:
    def test_create_instance(self):
        config = Config(devices=[])
