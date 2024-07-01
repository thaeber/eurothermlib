import pint

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
        config = SerialPortConfig(port='COM1')
        assert config.port == 'COM1'
        assert config.baudRate == 19200


class TestDeviceConfig:
    def test_create_default_instance(self):
        config = DeviceConfig(
            name='dummy', unitAddress=1, connection=SerialPortConfig(port='COM2')
        )
        assert config.name == 'dummy'
        assert config.unitAddress == 1
        assert config.sampling_rate == pint.Quantity('1Hz')
        assert config.driver == 'simulate'
        assert config.connection.port == 'COM2'
        assert config.connection.baudRate == 19200


class TestConfig:
    def test_create_instance(self):
        config = Config(devices=[])
