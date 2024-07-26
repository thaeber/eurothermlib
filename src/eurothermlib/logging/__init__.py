import logging
import logging.handlers
from enum import IntFlag, auto
from pathlib import Path

from omegaconf import OmegaConf


class FileLoggingMode(IntFlag):
    NONE = auto()
    SERVER = auto()
    CLIENT = auto()


# logging config
def configure_logging(mode: FileLoggingMode):
    app_logging_config = """
    app_logging:
        version: 1
        formatters:
            simple:
                format: "[%(asctime)s][%(levelname)s] %(message)s"
                datefmt: "%Y-%m-%d %H:%M:%S"
            detailed:
                format: "[%(asctime)s][%(levelname)s][%(thread)s][%(filename)s:%(lineno)d] - %(message)s"
                datefmt: "%Y-%m-%d %H:%M:%S"
            rich:
                format: "[%(thread)s] %(message)s"
        handlers:
            console:
                class: rich.logging.RichHandler
                formatter: rich
                markup: False
            client:
                class: eurothermlib.logging.TimedRotatingFileHandler
                formatter: simple
                filename: .log/eurotherm.client.log
                encoding: utf-8
                when: "h"
                interval: 1
            server:
                class: eurothermlib.logging.TimedRotatingFileHandler
                formatter: simple
                filename: .log/eurotherm.server.log
                encoding: utf-8
                when: "h"
                interval: 1
        root:
            level: INFO
            handlers:
                - console
        disable_existing_loggers: false
    """
    cfg = OmegaConf.to_object(
        OmegaConf.create(app_logging_config).app_logging,
    )
    match mode:
        case FileLoggingMode.SERVER:
            cfg['root']['handlers'].append('server')
        case FileLoggingMode.CLIENT:
            cfg['root']['handlers'].append('client')

    logging.config.dictConfig(cfg)


class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, filename, **kwargs):
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        super().__init__(filename, **kwargs)
