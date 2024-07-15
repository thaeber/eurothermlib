from dataclasses import dataclass
from datetime import datetime
import logging
from abc import ABC, abstractmethod
from enum import IntEnum, IntFlag, auto
from typing import cast

import numpy as np

from ..utils import DimensionlessQ, TemperatureQ, VoltageQ

# ureg = pint.application_registry.get()
logger = logging.getLogger(__name__)


class InstrumentStatus(IntFlag):
    Ok = auto()
    Alarm1 = auto()
    Alarm2 = auto()
    Alarm3 = auto()
    Alarm4 = auto()
    SensorBreak = auto()
    LoopBreak = auto()
    HeaterFail = auto()
    LoadFail = auto()
    ProgramEnd = auto()
    PVOutOfRange = auto()
    NewAlarm = auto()
    TimerRampRunning = auto()
    RemoteSPFail = auto()
    LocalRemoteSPSelect = auto()


class RemoteSetpointState(IntEnum):
    DISBALE = 0
    ENABLE = 1


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
    def status(self) -> InstrumentStatus:
        return InstrumentStatus.Ok

    def get_process_values(self) -> ProcessValues:
        return ProcessValues(
            timestamp=datetime.now(),
            processValue=self.process_value,
            setpoint=self.setpoint,
            workingSetpoint=self.working_setpoint,
            workingOutput=self.working_output,
            status=self.status,
        )

    @abstractmethod
    def toggle_remote_setpoint(self, state: RemoteSetpointState):
        pass

    @abstractmethod
    def write_remote_setpoint(self, value: TemperatureQ):
        pass

    @abstractmethod
    def acknowledge_all_alarms(self):
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
    def setpoint(self) -> TemperatureQ:
        return cast(TemperatureQ, self._setpoint)

    @property
    def working_setpoint(self) -> TemperatureQ:
        return cast(TemperatureQ, self._setpoint)

    @property
    def working_output(self):
        return DimensionlessQ(0.0, '%')

    def toggle_remote_setpoint(self, state: RemoteSetpointState):
        pass

    def write_remote_setpoint(self, value: TemperatureQ):
        pass

    def acknowledge_all_alarms(self):
        pass
