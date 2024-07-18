import logging
import threading
import time
from abc import ABCMeta
from dataclasses import dataclass
from datetime import datetime
from enum import IntFlag, auto
from typing import Callable, Dict, List, Optional

import numpy as np
import reactivex
import reactivex.operators as op
from google.protobuf.timestamp_pb2 import Timestamp
from reactivex.scheduler import ThreadPoolScheduler

from .. import controllers
from ..configuration import DeviceConfig
from ..controllers.controller import (
    InstrumentStatus,
    ProcessValues,
    RemoteSetpointState,
)
from ..utils import DimensionlessQ, TemperatureQ, TemperatureRateQ, TimeQ
from .proto import service_pb2


class TemperatureRampState(IntFlag):
    NoRamp = auto()
    Ramping = auto()
    Holding = auto()
    Stopped = auto()
    Finished = auto()


@dataclass
class TData:
    deviceName: str
    timestamp: datetime
    processValue: TemperatureQ
    setpoint: TemperatureQ
    workingSetpoint: TemperatureQ
    remoteSetpoint: TemperatureQ
    workingOutput: DimensionlessQ
    status: controllers.InstrumentStatus
    rampStatus: TemperatureRampState

    def to_grpc_response(self):
        timestamp = Timestamp()
        timestamp.FromDatetime(self.timestamp)
        response = service_pb2.ProcessValues(
            deviceName=self.deviceName,
            timestamp=timestamp,
            processValue=self.processValue.m_as('K'),
            setpoint=self.setpoint.m_as('K'),
            workingSetpoint=self.workingSetpoint.m_as('K'),
            remoteSetpoint=self.remoteSetpoint.m_as('K'),
            workingOutput=self.workingOutput.m_as('%'),
            status=int(self.status),
            rampStatus=int(self.rampStatus),
        )
        return response

    @staticmethod
    def from_grpc_response(response: service_pb2.ProcessValues):
        return TData(
            deviceName=response.deviceName,
            timestamp=response.timestamp.ToDatetime(),
            processValue=TemperatureQ(response.processValue, 'K'),  # type: ignore
            setpoint=TemperatureQ(response.setpoint, 'K'),  # type: ignore
            workingSetpoint=TemperatureQ(response.workingSetpoint, 'K'),  # type: ignore
            remoteSetpoint=TemperatureQ(response.remoteSetpoint, 'K'),  # type: ignore
            workingOutput=DimensionlessQ(response.workingOutput, '%'),  # type: ignore
            status=controllers.InstrumentStatus(response.status),
            rampStatus=TemperatureRampState(response.rampStatus),
        )


logger = logging.getLogger(__name__)
TEmitter = Callable[[TData], None]


class SingletonMeta(ABCMeta):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instance[cls]


class EurothermIO(metaclass=SingletonMeta):
    def __init__(self, cfg: List[DeviceConfig]) -> None:
        super().__init__()
        self.cfg = cfg
        self._lock = threading.RLock()
        self._threads: Dict[str, IOThread] = {}
        self._observable: Optional[reactivex.Subject[TData]] = None
        self._pool = ThreadPoolScheduler()

    def _iter_threads(self):
        for thread in self._threads.values():
            yield thread

    def _get_thread(self, device: str):
        with self._lock:
            if device not in self._threads:
                logger.error(f'[{repr(device)}] Unknown device name')
                return None
            else:
                return self._threads[device]

    def _ensure_observable(self):
        with self._lock:
            if self._observable is None:
                self._observable = reactivex.Subject[TData]()
        return self._observable

    def _emit(self, data: TData):
        observable = self._ensure_observable()
        observable.on_next(data)

    @property
    def observable(self):
        observable = self._ensure_observable()
        return observable.pipe(op.observe_on(self._pool))

    def start(self):
        with self._lock:
            if not self._threads:
                # spin up a thread for each device
                for device in self.cfg:
                    if device.name in self._threads:
                        msg = f'A device with the name {device.name} already exists'
                        logger.error(msg)
                        raise ValueError(msg)
                    try:
                        thread = IOThread(device, self._emit)
                        thread.start()
                        self._threads[device.name] = thread
                    except ValueError:
                        logger.warning(
                            (
                                f'Could not start acquisition thread '
                                f'for device: {device.name}'
                            )
                        )
            else:
                logger.debug('Acquisition threads already running.')

    def stop(self):
        self.complete()
        with self._lock:
            if not self._threads:
                return
            for thread in self._iter_threads():
                thread.cancel()
            for thread in self._iter_threads():
                thread.join()

            self._threads.clear()

    def complete(self):
        with self._lock:
            if self._observable is not None:
                self._observable.on_completed()
                self._observable = None

    def toggle_remote_setpoint(self, device: str, state: RemoteSetpointState):
        self._get_thread(device).toggle_remote_setpoint(state)

    def set_remote_setpoint(self, device: str, value: TemperatureQ):
        self._get_thread(device).remote_setpoint = value

    def start_temperature_ramp(
        self, device: str, to: TemperatureQ, rate: TemperatureRateQ
    ):
        observable = self._get_thread(device).start_temperature_ramp(to, rate)
        return observable.pipe(op.observe_on(self._pool))

    def acknowledge_all_alarms(self, device: str):
        if device == '*':
            logger.info('Acknowledge alarms on all devices')
            for thread in self._iter_threads():
                thread.acknowledge_all_alarms()
        else:
            self._get_thread(device).acknowledge_all_alarms()


class IOThread(threading.Thread):
    def __init__(
        self,
        device: DeviceConfig,
        emit: TEmitter,
    ):
        super().__init__()
        self._lock = threading.RLock()
        self.device = device
        self.cancel_event = threading.Event()
        self._emit = emit
        self.controller: controllers.EurothermController = (
            controllers.EurothermSimulator()
        )
        self._remote_setpoint = TemperatureQ(28.0, '°C')
        self._ramp_thread: Optional[TemperatureRampThread] = None

        match self.device.driver:
            case 'simulate':
                pass
            case 'generic':
                connection = controllers.ModbusSerialConnection(self.device.connection)
                self.controller = controllers.GenericEurothermController(
                    self.device.unitAddress, connection
                )
            # case 'model3208':
            #     self.controller = EurothermModel3208(None)
            case _:
                logger.error(f'Unknown device driver: {device.driver}')
                raise ValueError(f'Unknown device driver: {device.driver}')

    def join(self, timeout: float | None = None) -> None:
        with self._lock:
            if self._ramp_thread is not None:
                self._ramp_thread.join(timeout)
        return super().join(timeout)

    def cancel(self):
        with self._lock:
            if self._ramp_thread is not None:
                self._ramp_thread.cancel()
        self.cancel_event.set()

    @property
    def cancelled(self):
        return self.cancel_event.is_set()

    @property
    def remote_setpoint(self):
        with self._lock:
            return self._remote_setpoint

    @remote_setpoint.setter
    def remote_setpoint(self, value: TemperatureQ):
        with self._lock:
            self._remote_setpoint = value

    @property
    def ramp_status(self):
        with self._lock:
            if self._ramp_thread is None:
                return TemperatureRampState.NoRamp
            elif self._ramp_thread.cancelled:
                return TemperatureRampState.Stopped
            elif not self._ramp_thread.is_alive():
                return TemperatureRampState.Finished
            else:
                return TemperatureRampState.Ramping

    def toggle_remote_setpoint(self, state: RemoteSetpointState):
        if not self.cancelled:
            self.controller.toggle_remote_setpoint(state)

    def acknowledge_all_alarms(self):
        if not self.cancelled:
            self.controller.acknowledge_all_alarms()

    def start_temperature_ramp(self, to: TemperatureQ, rate: TemperatureRateQ):
        logger.debug('Acquire lock...')
        with self._lock:
            logger.debug('...lock acquired.')
            if self.ramp_status == TemperatureRampState.Ramping:
                msg = 'Found active temperature ramp: {0:.2f~P} to {1:.2f~P} @ {2:.2f~P}'.format(
                    self._ramp_thread.T_start,
                    self._ramp_thread.T_end,
                    self._ramp_thread.rate,
                )
                logger.info(msg)
                logger.info('Cancelling active ramp...')
                self._ramp_thread.cancel()
                self._ramp_thread.join()
                logger.info('...ramp cancelled')

            # read current temperature
            T_start = self.controller.get_process_values().processValue

            # start new ramp
            msg = (
                'Starting temperature ramp: {0:.2f~P} to {1:.2f~P} @ {2:.2f~P}'.format(
                    T_start, to, rate
                )
            )
            logger.info(msg)
            self._ramp_thread = TemperatureRampThread(self, T_start, to, rate)
            self._ramp_thread.start()

            return self._ramp_thread.observable

    def emit(self, values: ProcessValues):
        data = TData(
            deviceName=self.device.name,
            timestamp=values.timestamp,
            processValue=values.processValue,
            setpoint=values.setpoint,
            workingSetpoint=values.workingSetpoint,
            remoteSetpoint=self.remote_setpoint,
            workingOutput=values.workingOutput,
            status=values.status,
            rampStatus=self.ramp_status,
        )
        self._emit(data)

    def run(self):
        logger.info(f'{self.__class__.__name__} started for device {self.device.name}')
        # do actual work
        try:
            self.do_work()
        except Exception:
            logger.exception(f'Exception occurred in task: {self.__class__.__name__}')

    def do_work(self):
        time.time()
        sampling_interval = 1.0 / self.device.sampling_rate.m_as('Hz')
        while not self.cancel_event.is_set():
            # read current process values
            values = self.controller.get_process_values()

            # emit process values
            self.emit(values)

            # write remote setpoint
            if InstrumentStatus.LocalRemoteSPSelect in values.status:
                self.controller.write_remote_setpoint(self.remote_setpoint)

            time.sleep(sampling_interval)


class TemperatureRampThread(threading.Thread):
    def __init__(
        self,
        iothread: IOThread,
        T_start: TemperatureQ,
        T_end: TemperatureQ,
        temprature_rate: TemperatureRateQ,
    ):
        super().__init__()
        self.cancel_event = threading.Event()
        self._iothread = iothread
        self.T_start = T_start.to('K')
        self.T_end = T_end.to('K')
        self.rate = temprature_rate.to('K/min')
        self.observable = reactivex.Subject[TemperatureQ]()

    def cancel(self):
        self.cancel_event.set()

    @property
    def cancelled(self):
        return self.cancel_event.is_set()

    def run(self):
        logger.info(
            f'{self.__class__.__name__} started for device {self._iothread.device.name}'
        )
        # do actual work
        try:
            self.do_work()
        except Exception:
            logger.exception(f'Exception occurred in task: {self.__class__.__name__}')

    def do_work(self):
        time.time()
        sampling_interval = 1.0  # seconds
        t0 = time.monotonic()  # monotonic clock in fractional seconds
        current = self.T_start
        sign = np.sign(self.T_end.m_as('K') - self.T_start.m_as('K'))
        while not self.cancel_event.is_set():
            # elapsed time
            elapsed: TimeQ = TimeQ(time.monotonic() - t0, 's')

            # calculate new setpoint
            current: TemperatureQ = self.T_start + sign * self.rate * elapsed

            if sign * (current - self.T_end) > 0:
                self._iothread.remote_setpoint = self.T_end
                self.observable.on_next(self.T_end)
                break  # terminate loop
            else:
                self._iothread.remote_setpoint = current
                self.observable.on_next(current)

            time.sleep(sampling_interval)

        # signal completion of temperature ramp
        self.observable.on_completed()
        self.observable.dispose()
