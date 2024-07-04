from pathlib import Path

import pint

from eurothermlib.configuration import (
    Config,
    DeviceConfig,
    SerialPortConfig,
    ServerConfig,
    get_configuration,
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
        Config(devices=[])

    def test_get_configuration(self):
        filename = Path(__file__).parent / 'data' / '.eurotherm.yaml'
        config = get_configuration(filename=filename)

        assert str(config.server.ip) == '127.0.10.1'
        assert config.server.port == 50066
        assert config.devices[0].name == 'my_reactor'
        assert config.devices[0].sampling_rate == pint.Quantity('3.5Hz')

    def test_get_configuration_with_dotlist(self):
        filename = Path(__file__).parent / 'data' / '.eurotherm.yaml'
        config = get_configuration(
            filename=filename, cmd_args=['server.port=11111', 'devices[0].name=test']
        )

        assert str(config.server.ip) == '127.0.10.1'
        assert config.server.port == 11111
        assert config.devices[0].name == 'test'
        assert config.devices[0].sampling_rate == pint.Quantity('3.5Hz')

    def test_get_configuration_with_app_logging(self):
        filename = Path(__file__).parent / 'data' / '.eurotherm.app-logging.yaml'
        config = get_configuration(filename=filename)

        assert str(config.server.ip) == '127.0.10.1'
        assert config.server.port == 50066
        assert config.devices[0].name == 'my_reactor'
        assert config.devices[0].sampling_rate == pint.Quantity('3.5Hz')
