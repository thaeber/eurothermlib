from dataclasses import dataclass
from datetime import datetime
import logging
import struct
from abc import ABC, abstractmethod
from enum import IntEnum, IntFlag
from typing import cast

import numpy as np
import tenacity
from pymodbus import ModbusException
from serial import Serial

from .configuration import DeviceConfig
from .connection import ModbusSerial
from .utils import DimensionlessQ, TemperatureQ, VoltageQ

# ureg = pint.application_registry.get()
logger = logging.getLogger(__name__)


class InstrumentStatus(IntFlag):
    NONE = 0x00
    Alarm1 = 0x0001
    Alarm2 = 0x0002
    Alarm3 = 0x0004
    Alarm4 = 0x0008
    SensorBreak = 0x0020
    LoopBreak = 0x0040
    HeaterFail = 0x0080
    LoadFail = 0x0100
    ProgramEnd = 0x0200
    PVOutOfRange = 0x0400
    NewAlarm = 0x1000
    TimerRampRunning = 0x2000
    RemoteSPFail = 0x4000


@dataclass
class ProcessValues:
    timestamp: datetime
    processValue: TemperatureQ
    setpoint: TemperatureQ
    workingSetpoint: TemperatureQ
    workingOutput: DimensionlessQ
    status: InstrumentStatus


class EurothermController(ABC):
    @property
    @abstractmethod
    def process_value(self) -> TemperatureQ:
        pass

    @property
    @abstractmethod
    def measured_value(self) -> VoltageQ:
        pass

    @property
    @abstractmethod
    def working_setpoint(self) -> TemperatureQ:
        pass

    @property
    @abstractmethod
    def working_output(self) -> DimensionlessQ:
        pass

    def status(self) -> InstrumentStatus:
        return InstrumentStatus.NONE

    @abstractmethod
    def get_process_values(self) -> ProcessValues:
        pass


class EurothermSimulator(EurothermController):
    def __init__(self):
        self._process_value = TemperatureQ(20, 'degC')
        self._setpoint = self._process_value

    @property
    def process_value(self):
        return cast(TemperatureQ, self._process_value)

    @property
    def measured_value(self):
        T = self._process_value.m_as('degC')

        # thermo voltage of Type K thermocouple [T (°C), U (mV)]
        type_k_data = np.array(
            [
                [0, 0],
                [100, 4.096],
                [200, 8.138],
                [300, 12.209],
                [400, 16.397],
                [500, 20.644],
                [600, 24.905],
                [700, 29.129],
                [800, 33.275],
                [900, 37.326],
                [1000, 41.276],
                [1100, 45.119],
                [1200, 48.838],
                [1250, 50.644],
                [1300, 52.410],
            ]
        )
        voltage = np.interp(T, *type_k_data.T)
        return cast(VoltageQ, VoltageQ(voltage, 'mV'))

    @property
    def working_setpoint(self) -> TemperatureQ:
        return cast(TemperatureQ, self._setpoint)

    @property
    def working_output(self):
        return DimensionlessQ(0.0, '%')

    def get_process_values(self) -> ProcessValues:
        pass


def _log_attemp_number(retry_state):
    logging.error(f"Retrying: {retry_state.attempt_number}...")


class GenericAddress(IntEnum):
    PVIN = 1  # process value (current temperature) [°C]
    TGSP = 2  # (manual) target setpoint (do not write)
    WRKOP = 4  # working output power level [%]
    WKGSP = 5  # working setpoint (during remote control or ramping) [°C]
    MVIN = 202  # measured thermocouple input value [mV]
    LR = 276  # Enable/disable local external (COM) setpoint selection
    RmSP = 26  # External (COM) setpoint (writable) [°C]
    STAT = 75  # Instrument status (bitmap)
    AcALL = 274  # Acknowledge all alarms (1=acknowledge)


class GenericEurothermController(EurothermController):
    def __init__(self, device: DeviceConfig):
        self.device = device
        self.connection = ModbusSerial(device.connection)

    @tenacity.retry(
        reraise=True,
        stop=tenacity.stop_after_attempt(3),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARN),
        # after=_log_attemp_number,
    )
    def _read_int_registers(self, address, num_registers=1):
        try:
            response = self.connection.read_holding_registers(
                self.device.unitAddress,
                address,
                num_registers,
            ).result()
        except ModbusException as ex:
            raise ex
        if response.isError():
            raise ModbusException(response.message)
        else:
            return response.registers

    def _read_float_registers(self, address, num_registers=1):
        registers = self._read_int_registers(0x8000 + 2 * address, 2 * num_registers)
        return self._unpack(registers)

    def _unpack(self, registers):
        return [
            struct.unpack('f', struct.pack("HH", registers[k + 1], registers[k]))[0]
            for k in range(0, len(registers), 2)
        ]

    @property
    def process_value(self) -> TemperatureQ:
        return TemperatureQ(self._read_float_registers(GenericAddress.PVIN)[0], '°C')

    @property
    def measured_value(self) -> VoltageQ:
        return VoltageQ(self._read_float_registers(GenericAddress.MVIN)[0], 'mV')

    @property
    def working_setpoint(self) -> TemperatureQ:
        return TemperatureQ(self._read_float_registers(GenericAddress.WKGSP)[0], '°C')

    @property
    def working_output(self) -> DimensionlessQ:
        return DimensionlessQ(self._read_float_registers(GenericAddress.WRKOP)[0], '%')

    @property
    def status(self) -> InstrumentStatus:
        bits = self._read_int_registers(address=GenericAddress.STAT)[0]

        def is_set(bits, bit):
            mask = 1 << bit
            return (bits & mask) == mask

        status = InstrumentStatus.NONE
        if is_set(bits, 0):  # Bit 0
            status |= InstrumentStatus.Alarm1
        if is_set(bits, 1):  # Bit 1
            status |= InstrumentStatus.Alarm2
        if is_set(bits, 2):  # Bit 2
            status |= InstrumentStatus.Alarm3
        if is_set(bits, 3):  # Bit 3
            status |= InstrumentStatus.Alarm4
        if is_set(bits, 5):  # Bit 5
            status |= InstrumentStatus.SensorBreak
        if is_set(bits, 6):  # Bit 6
            status |= InstrumentStatus.LoopBreak
        if is_set(bits, 7):  # Bit 7
            status |= InstrumentStatus.HeaterFail
        if is_set(bits, 8):  # Bit 8
            status |= InstrumentStatus.LoadFail
        if is_set(bits, 9):  # Bit 9
            status |= InstrumentStatus.ProgramEnd
        if is_set(bits, 10):  # Bit 10
            status |= InstrumentStatus.PVOutOfRange
        if is_set(bits, 12):  # Bit 12
            status |= InstrumentStatus.NewAlarm
        if is_set(bits, 13):  # Bit 13
            status |= InstrumentStatus.TimerRampRunning
        if is_set(bits, 14):  # Bit 14
            status |= InstrumentStatus.RemoteSPFail

        return status

    def get_process_values(self) -> ProcessValues:
        registers = self._read_float_registers(
            address=GenericAddress.PVIN, num_registers=5
        )
        timestamp = datetime.now()

        return ProcessValues(
            timestamp=timestamp,
            processValue=TemperatureQ(registers[GenericAddress.PVIN - 1], '°C'),
            setpoint=TemperatureQ(registers[GenericAddress.TGSP - 1], '°C'),
            workingSetpoint=TemperatureQ(registers[GenericAddress.WKGSP - 1], '°C'),
            workingOutput=DimensionlessQ(registers[GenericAddress.WRKOP - 1], '%'),
            status=self.status,
        )


class EurothermModel3208(GenericEurothermController):
    def __init__(self, port: Serial):
        pass
