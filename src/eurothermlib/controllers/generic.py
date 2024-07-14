import logging
import struct
from datetime import datetime
from enum import IntEnum
from typing import Optional

import tenacity
from pymodbus import ModbusException

from ..utils import DimensionlessQ, TemperatureQ
from .connection import ModbusSerialConnection
from .controller import (
    EurothermController,
    InstrumentStatus,
    ProcessValues,
    RemoteSetpointState,
)

# ureg = pint.application_registry.get()
logger = logging.getLogger(__name__)


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
    def __init__(self, unit_address: int, connection: ModbusSerialConnection):
        self._unit_address = unit_address
        self._connection = connection

    # region internal

    @tenacity.retry(
        reraise=True,
        stop=tenacity.stop_after_attempt(3),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARN),
    )
    def _read_int_registers(self, address, num_registers=1):
        try:
            response = self._connection.read_holding_registers(
                self._unit_address,
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

    @tenacity.retry(
        reraise=True,
        stop=tenacity.stop_after_attempt(3),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARN),
    )
    def _write_int_register(self, address: int, value: int):
        try:
            response = self._connection.write_holding_register(
                self._unit_address,
                address,
                value,
            ).result()
        except ModbusException as ex:
            raise ex
        if response.isError():
            raise ModbusException(response.message)

    # endregion

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

        remoteSP = self._read_int_registers(address=GenericAddress.LR)[0]
        if remoteSP:
            status |= InstrumentStatus.LocalRemoteSPSelect

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

    def select_remote_setpoint(self, state: RemoteSetpointState):
        match state:
            case RemoteSetpointState.ENABLE:
                self._write_int_register(GenericAddress.LR, 1)
            case RemoteSetpointState.DISBALE:
                self._write_int_register(GenericAddress.LR, 0)

    def write_remote_setpoint(self, value: TemperatureQ):
        _value = value.m_as('degC')
        _value = int(round(_value))
        self._write_int_register(GenericAddress.RmSP, _value)

    def acknowledge_all_alarms(self):
        self._write_int_register(GenericAddress.AcALL, int(1))
