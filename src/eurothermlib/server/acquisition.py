import abc
import logging
import threading
import time
from abc import ABCMeta
from datetime import datetime
from typing import Callable, List, Optional

import numpy as np
import numpy.typing as npt
import reactivex
import reactivex.operators as op
import xarray as xr
from reactivex.scheduler import ThreadPoolScheduler

from ._configuration import DeviceConfig, TCLoggerConfig

logger = logging.getLogger(__name__)
TEmitter = Callable[[xr.DataArray], None]


class SingletonMeta(ABCMeta):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instance[cls]


class TemperatureIO(metaclass=SingletonMeta):

    def __init__(self, cfg: TCLoggerConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self._lock = threading.Lock()
        self._threads: List[IOThreadBase] = []
        self._observable = reactivex.Subject[xr.DataArray]()
        self._pool = ThreadPoolScheduler()

    @property
    def observable(self):
        return self._observable.pipe(op.observe_on(self._pool))

    def _names(self):
        for device in self.cfg.devices:
            for channel in device.channels:
                yield channel.name

    @property
    def names(self) -> List[str]:
        return list(self._names())

    @property
    def number_of_channels(self) -> int:
        return len(self.names)

    def start(self):
        with self._lock:
            if not self._threads:
                # spin up a thread for each device
                for device in self.cfg.devices:
                    if device.simulate:
                        thread = SimulateIOThread(device, self._emit)
                    elif device.driver == 'nidaqmx':
                        thread = NIDAQmxIOThread(device, self._emit)
                    else:
                        logger.error(f'Unknown device driver: {device.name}')
                        continue
                    thread.start()
                    self._threads.append(thread)
            else:
                logger.debug('Acquisition threads already running.')

    def stop(self):
        with self._lock:
            if not self._threads:
                return
            for thread in self._threads:
                thread.cancel()
            for thread in self._threads:
                thread.join()

            self._threads = []

    def complete(self):
        self.stop()
        self._observable.on_completed()

    def _emit(self, da: xr.DataArray):
        self._observable.on_next(da)


class IOThreadBase(threading.Thread):

    def __init__(
        self,
        device: DeviceConfig,
        emit: TEmitter,
    ):
        super().__init__()
        # self.daemon = True  # ensures that thread
        self.device = device
        self.channel_names = [d.name for d in device.channels]
        self.cancel_event = threading.Event()
        self._emit = emit

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

    def emit(self, values: npt.NDArray[np.float64], unit: str | pint.Unit):
        da = xr.DataArray(
            np.atleast_2d(values),
            dims=('time', 'channel'),
            coords=dict(
                time=[np.datetime64(datetime.now(), 'ms')],
                channel=self.channel_names,
            ),
        )
        da = da.pint.quantify(unit)
        self._emit(da)

    def run(self):
        logger.info(f'{self.__class__.__name__} started for device {self.device.name}')
        # do actual work
        try:
            self.do_work()
        except:
            logger.exception(f'Exception occurred in task: {self.__class__.__name__}')

    @abc.abstractmethod
    def do_work(self):
        pass


class SimulateIOThread(IOThreadBase):

    def __init__(
        self,
        cfg: DeviceConfig,
        emit: TEmitter,
    ):
        super().__init__(cfg, emit)
        self.number_of_channels = len(cfg.channels)

    def do_work(self):
        start = time.time()
        while not self.cancel_event.is_set():
            # data = np.random.uniform(size=self.number_of_channels)
            data = np.random.normal(size=self.number_of_channels)
            data += 3 * np.sin((time.time() - start) / 60.0 * 2 * np.pi)
            data += 20.0
            self.emit(data.copy(), units.degC)
            time.sleep(1 / self.device.sampling_rate)
