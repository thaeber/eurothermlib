import logging
import logging.config
from datetime import datetime
from ipaddress import IPv4Address
from os import PathLike
from pathlib import Path
from typing import Annotated, List, Literal, Optional

import serial
from omegaconf import OmegaConf
from pydantic import BaseModel, Field

from .utils import TypedQuantity

OmegaConf.register_new_resolver('now', lambda fmt: datetime.now().strftime(fmt))

# _app_logging_conf = Path('./conf/app_logging.yaml')
# if _app_logging_conf.exists():
#     _conf = OmegaConf.load(_app_logging_conf)
#     logging.config.dictConfig(OmegaConf.to_container(_conf))  # type: ignore

logger = logging.getLogger(__name__)


class ServerConfig(BaseModel):
    ip: IPv4Address = IPv4Address('127.0.0.1')
    port: int = 50061


class SerialPortConfig(BaseModel):
    port: str = 'COM1'
    baudRate: int = 19200


Driver = Literal['simulate', 'model3208']


class DeviceConfig(BaseModel):
    name: str
    unitAddress: int = 1
    connection: SerialPortConfig = SerialPortConfig()
    sampling_rate: Annotated[
        TypedQuantity['1/[time]'], Field(validate_default=True)
    ] = '1 Hz'
    driver: Driver = 'simulate'


class Config(BaseModel):
    server: ServerConfig = ServerConfig()
    devices: List[DeviceConfig]


# @dataclass
# class LoggingConfig:
#     # target path and filename
#     dir: str = './outputs/tclogger/${now:%Y-%m-%d}'
#     filename: str = '${now:%Y-%m-%dT%H-%M-%S}.csv'
#     mode: str = 'w'
#     # formatting
#     unit: str = "kelvin"
#     format: str = "%.2f"
#     separator: str = ";"
#     # timing
#     write_interval: float = 0.0  # [s]; write readings in groups at given interval


def get_configuration(
    cmd_args: Optional[List[str]] = None,
    filename: str | PathLike = '.eurotherm.yaml',
    use_cli=False,
):
    cfg = OmegaConf.load(Path(filename))
    if use_cli:
        cfg.merge_with_cli()
    if cmd_args is not None:
        cfg.merge_with_dotlist(cmd_args)

    return Config.model_validate(OmegaConf.to_container(cfg, resolve=True))
