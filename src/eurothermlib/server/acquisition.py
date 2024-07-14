import logging
import threading
import time
from abc import ABCMeta
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional

import reactivex
import reactivex.operators as op
from google.protobuf.timestamp_pb2 import Timestamp
from reactivex.scheduler import ThreadPoolScheduler

from .. import controllers
from ..configuration import DeviceConfig
from ..controllers.controller import RemoteSetpointState
from ..utils import DimensionlessQ, TemperatureQ
from .proto import service_pb2


@dataclass
class TData:
    deviceName: str
    timestamp: datetime
    processValue: TemperatureQ
    setpoint: TemperatureQ
    workingSetpoint: TemperatureQ
    workingOutput: DimensionlessQ
    status: controllers.InstrumentStatus

    def to_grpc_response(self):
        timestamp = Timestamp()
        timestamp.FromDatetime(self.timestamp)
        response = service_pb2.ProcessValues(
            deviceName=self.deviceName,
            timestamp=timestamp,
            processValue=self.processValue.m_as('K'),
            setpoint=self.setpoint.m_as('K'),
            workingSetpoint=self.workingSetpoint.m_as('K'),
            workingOutput=self.workingOutput.m_as('%'),
            status=int(self.status),
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
            workingOutput=DimensionlessQ(response.workingOutput, '%'),  # type: ignore
            status=controllers.InstrumentStatus(response.status),
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
        self._lock = threading.Lock()
        self._threads: Dict[str, IOThreadBase] = {}
        self._observable: Optional[reactivex.Subject[TData]] = None
        self._pool = ThreadPoolScheduler()

    def _iter_threads(self):
        for thread in self._threads.values():
            yield thread

    def _get_thread(self, device: str):
        with self._lock:
            if not device in self._threads:
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
                        thread = IOThreadBase(device, self._emit)
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

    def select_remote_setpoint(self, device: str, state: RemoteSetpointState):
        self._get_thread(device).select_remote_setpoint(state)

    def acknowledge_all_alarms(self, device: str):
        if device == '*':
            logger.info('Acknowledge alarms on all devices')
            for thread in self._iter_threads():
                thread.acknowledge_all_alarms()
        else:
            self._get_thread(device).acknowledge_all_alarms()


class IOThreadBase(threading.Thread):
    def __init__(
        self,
        device: DeviceConfig,
        emit: TEmitter,
    ):
        super().__init__()
        self._lock = threading.Lock()
        self.device = device
        self.cancel_event = threading.Event()
        self._emit = emit
        self.controller: controllers.EurothermController = (
            controllers.EurothermSimulator()
        )

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

    def cancel(self):
        self.cancel_event.set()

    @property
    def cancelled(self):
        return self.cancel_event.is_set()

    def wait_for_termination(
        self,
        timeout: Optional[float] = None,
        polling_interval: float = 0.2,
    ):
        start = time.monotonic()
        while self.is_alive():
            self.join(polling_interval)
            if (timeout is not None) and (time.monotonic() - start >= timeout):
                return

    def emit(self):
        values = self.controller.get_process_values()
        data = TData(
            deviceName=self.device.name,
            timestamp=values.timestamp,
            processValue=values.processValue,
            setpoint=values.setpoint,
            workingSetpoint=values.workingSetpoint,
            workingOutput=values.workingOutput,
            status=values.status,
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
            self.emit()
            time.sleep(sampling_interval)

    def select_remote_setpoint(self, state: RemoteSetpointState):
        if not self.cancelled:
            self.controller.select_remote_setpoint(state)

    def acknowledge_all_alarms(self):
        if not self.cancelled:
            self.controller.acknowledge_all_alarms()
