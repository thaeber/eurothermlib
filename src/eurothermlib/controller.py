from abc import ABC, abstractmethod
from typing import TypeAlias, cast

import numpy as np
import pint
from serial import Serial

from .utils import TypedQuantity

ureg = pint.application_registry.get()


class VoltageQ(TypedQuantity['[electric_potential]']):
    pass


TemperatureQ: TypeAlias = TypedQuantity['[temperature]']
DimensionlessQ: TypeAlias = TypedQuantity['[]']


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
    def working_setpoint(self) -> pint.Quantity:
        raise NotImplementedError()

    @property
    def working_output(self) -> pint.Quantity:
        raise NotImplementedError()


class EurothermModel3208(EurothermController):
    def __init__(self, port: Serial):
        pass
