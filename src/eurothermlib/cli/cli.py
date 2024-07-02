import logging
import click
from rich.traceback import install
from rich.pretty import pretty_repr

from ..configuration import Config, DeviceConfig, get_configuration

install()


@click.group
def cli():
    config = get_configuration()
    if config.app_logging is not None:
        logging.config.dictConfig(config.app_logging)
    logging.debug(f'Using configuration:')
    logging.debug(pretty_repr(config.model_dump()))
