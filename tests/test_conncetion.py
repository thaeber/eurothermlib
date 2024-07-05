from eurothermlib.configuration import SerialPortConfig
from eurothermlib.controllers import ModbusSerialConnection


class TestModbusSerial:
    def test_ensure_single_connection_per_port(self):
        c1 = ModbusSerialConnection(SerialPortConfig(port='com1'))
        c2 = ModbusSerialConnection(SerialPortConfig(port='com2'))
        c3 = ModbusSerialConnection(SerialPortConfig(port='com1'))
        c4 = ModbusSerialConnection(SerialPortConfig(port='com2'))
        assert c1 is not c2
        assert c1 is c3
        assert c1 is not c4
        assert c2 is c4
