from dataclasses import dataclass
from datetime import datetime
import logging
from abc import ABC, abstractmethod
from enum import IntFlag
from typing import cast

import numpy as np

from ..utils import DimensionlessQ, TemperatureQ, VoltageQ

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
    def setpoint(self) -> TemperatureQ:
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

    def get_process_values(self) -> ProcessValues:
        return ProcessValues(
            timestamp=datetime.now(),
            processValue=self.process_value,
            setpoint=self.setpoint,
            workingSetpoint=self.working_setpoint,
            workingOutput=self.working_output,
            status=self.status,
        )


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
    def setpoint(self) -> TemperatureQ:
        return cast(TemperatureQ, self._setpoint)

    @property
    def working_setpoint(self) -> TemperatureQ:
        return cast(TemperatureQ, self._setpoint)

    @property
    def working_output(self):
        return DimensionlessQ(0.0, '%')
