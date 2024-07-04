from concurrent import futures
import logging
from .configuration import SerialPortConfig
from pymodbus.client import ModbusSerialClient

logger = logging.getLogger(__name__)


class ModbusSerial:
    __connections__ = {}

    def __init__(self, cfg: SerialPortConfig):
        self.client = ModbusSerialClient(cfg.port, baudrate=cfg.baudRate, strict=False)
        self.executor = futures.ThreadPoolExecutor(max_workers=1)

    def __new__(cls, cfg: SerialPortConfig):
        if cfg.port in ModbusSerial.__connections__:
            return ModbusSerial.__connections__[cfg.port]
        else:
            instance = super().__new__(cls)
            ModbusSerial.__connections__[cfg.port] = instance
            return instance

    def close(self):
        return self.client.close()

    def _do_read_holding_registers(
        self, unit_address: int, register_address: int, count: int
    ):
        logger.debug(
            (
                f'Read holding register(s): unit={unit_address},'
                f'register={register_address}, count={count}'
            )
        )
        return self.client.read_holding_registers(
            address=register_address,
            count=count,
            slave=unit_address,
        )

    def read_holding_registers(
        self, unit_address: int, register_address: int, num_registers: int = 1
    ):
        return self.executor.submit(
            self._do_read_holding_registers,
            unit_address,
            register_address,
            num_registers,
        )
