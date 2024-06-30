import logging
import logging.config
from datetime import datetime
from ipaddress import IPv4Address
from typing import List, Literal

import serial
from omegaconf import OmegaConf
from pydantic import BaseModel

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


class DeviceConfig(BaseModel):
    unitAddress: int = 1
    connection: SerialPortConfig = SerialPortConfig()
    sampling_rate: float = 1.0  # [Hz]
    simulate: bool = True


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


# def get_configuration(
#     cmd_args: Optional[List[str]] = None,
#     filename='./conf/tclogger.yaml',
#     use_cli=False,
# ) -> TCLoggerConfig:
#     cfg: DictConfig = OmegaConf.structured(TCLoggerConfig)
#     try:
#         if Path(filename).exists():
#             cfg.merge_with(OmegaConf.load(filename))
#         if use_cli:
#             cfg.merge_with_cli()
#         if cmd_args is not None:
#             cfg.merge_with_dotlist(cmd_args)
#     except ConfigAttributeError as ex:
#         logger.critical("Invalid configuration option.", exc_info=ex)
#         raise ex

#     return cfg  # type: ignore
