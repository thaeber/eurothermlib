import logging
import logging.config
from datetime import datetime
from ipaddress import IPv4Address
from os import PathLike
from pathlib import Path
from typing import Annotated, Any, Dict, List, Literal, Optional

from omegaconf import OmegaConf
from pydantic import BaseModel, ConfigDict, Field, model_validator
from rich.pretty import pretty_repr

from .utils import FrequencyQ, TimeQ

logger = logging.getLogger(__name__)
OmegaConf.register_new_resolver('now', lambda fmt: datetime.now().strftime(fmt))


class ServerConfig(BaseModel):
    ip: IPv4Address = IPv4Address('127.0.0.1')
    port: int = 50061
    timeout: Annotated[TimeQ, Field(validate_default=True)] = '5s'


class SerialPortConfig(BaseModel):
    port: str = 'COM1'
    baudRate: int = 19200


Driver = Literal['simulate', 'generic', 'model3208']


class DeviceConfig(BaseModel):
    name: str
    unitAddress: int = 1
    connection: SerialPortConfig = SerialPortConfig()
    sampling_rate: Annotated[FrequencyQ, Field(validate_default=True)] = '1 Hz'
    driver: Driver = 'simulate'


class LoggingConfig(BaseModel):
    directory: str = './output/{:%Y-%m-%d}'
    filename: str = 'eurotherm-{:%Y-%m-%dT%H-%M-%S}.csv'
    format: str = "%.6g"
    separator: str = ";"
    rotate_every: Annotated[TimeQ, Field(validate_default=True)] = '1min'
    write_interval: Annotated[TimeQ, Field(validate_default=True)] = '10s'
    columns: List[str] = [
        'timestamp',
        'processValue',
        'workingOutput',
        'workingSetpoint',
    ]
    units: Dict[str, str] = {
        'processValue': 'K',
        'workingOutput': '%',
        'workingSetpoint': 'K',
    }

    @model_validator(mode='after')
    def check_time_intervals(self):
        if self.write_interval >= self.rotate_every:
            raise ValueError(
                (
                    f'The write interval of data packets '
                    f'(write_interval={self.write_interval:~P}) must be '
                    f'shorter than the rotation interval of data files '
                    f'(rotate_every={self.rotate_every:~P})'
                )
            )
        return self

    @model_validator(mode='after')
    def check_formatting(self):
        try:
            self.directory.format(datetime.now())
        except:
            raise ValueError(
                f'Cannot format directory name with current date/time: {self.directory}'
            )
        try:
            self.filename.format(datetime.now())
        except:
            raise ValueError(
                f'Cannot format directory name with current date/time: {self.filename}'
            )
        return self


class Config(BaseModel):
    model_config = ConfigDict(extra='forbid')
    server: ServerConfig = ServerConfig()
    devices: List[DeviceConfig]
    logging: LoggingConfig = LoggingConfig()


def get_configuration(
    *,
    cmd_args: Optional[List[str]] = None,
    filename: str | PathLike = '.eurotherm.yaml',
    use_cli=False,
):
    logger.info(f'Loading configuration from: {filename}')
    cfg = OmegaConf.load(Path(filename))
    if use_cli:
        cfg.merge_with_cli()
    if cmd_args is not None:
        cfg.merge_with_dotlist(cmd_args)

    result = Config.model_validate(OmegaConf.to_container(cfg, resolve=True))
    logger.debug('Current configuration:')
    logger.debug(pretty_repr(result))

    return result
