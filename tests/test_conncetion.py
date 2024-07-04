from eurothermlib.configuration import SerialPortConfig
from eurothermlib.connection import ModbusSerial


class TestModbusSerial:
    def test_ensure_single_connection_per_port(self):
        c1 = ModbusSerial(SerialPortConfig(port='com1'))
        c2 = ModbusSerial(SerialPortConfig(port='com2'))
        c3 = ModbusSerial(SerialPortConfig(port='com1'))
        c4 = ModbusSerial(SerialPortConfig(port='com2'))
        assert c1 is not c2
        assert c1 is c3
        assert c1 is not c4
        assert c2 is c4
