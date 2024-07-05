import logging
import threading
import time
from abc import ABCMeta
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List, Optional

import reactivex
import reactivex.operators as op
from google.protobuf.timestamp_pb2 import Timestamp
from reactivex.scheduler import ThreadPoolScheduler

from ..configuration import DeviceConfig
from ..controllers import EurothermController, EurothermSimulator, InstrumentStatus
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
    status: InstrumentStatus

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
            status=response.status,
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
        self._threads: List[IOThreadBase] = []
        self._observable: Optional[reactivex.Subject[TData]] = None
        self._pool = ThreadPoolScheduler()

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

    @property
    def names(self) -> List[str]:
        return list([c.name for c in self.cfg])

    @property
    def number_of_channels(self) -> int:
        return len(self.names)

    def start(self):
        with self._lock:
            if not self._threads:
                # spin up a thread for each device
                for device in self.cfg:
                    try:
                        thread = IOThreadBase(device, self._emit)
                        thread.start()
                        self._threads.append(thread)
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
            for thread in self._threads:
                thread.cancel()
            for thread in self._threads:
                thread.join()

            self._threads = []

    def complete(self):
        with self._lock:
            if self._observable is not None:
                self._observable.on_completed()
                self._observable = None


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
        self.controller: EurothermController = EurothermSimulator()

        match self.device.driver:
            case 'simulate':
                pass
            # case 'model3208':
            #     self.controller = EurothermModel3208(None)
            case _:
                logger.error(f'Unknown device driver: {device.driver}')
                raise ValueError(f'Unknown device driver: {device.driver}')

    def cancel(self):
        self.cancel_event.set()

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
        controller = self.controller
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
