import logging
import sys
import time
from concurrent import futures

import click
from omegaconf import OmegaConf
from omegaconf.errors import ConfigAttributeError
from rich.traceback import install

from . import servicer
from ..configuration import get_configuration
from .file_logger import TCFileLogger

logger = logging.getLogger(__name__)
install()

_cs = dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
)


@click.group
def cli():
    pass


@cli.command(context_settings=_cs)
@click.pass_context
@click.option(
    "--resolve",
    default=False,
    show_default=True,
    is_flag=True,
    help="Resolve variable interpolations before printing.",
)
def config(ctx, resolve):
    """Print the configuration."""
    try:
        cfg = get_configuration(cmd_args=ctx.args)
        print(OmegaConf.to_yaml(cfg, resolve=resolve))
    except ConfigAttributeError:
        pass


@cli.command(context_settings=_cs)
@click.pass_context
def start(ctx):
    """Starts the server for acquiring thermocouple readings."""
    logger.info('Starting server')

    cfg = get_configuration(cmd_args=ctx.args)
    if servicer.is_alive(cfg.server):
        logger.warning('Server is already running... do nothing.')
    else:
        future = servicer.serve(cfg)
        try:
            while True:
                _, not_done = futures.wait([future], timeout=2.0)
                if not not_done:
                    break
        except KeyboardInterrupt:
            logger.warning('Keyboard interrupt detected. Trying to stop server...')
            client = servicer.connect(cfg.server)
            client.stop_server()


@cli.command(context_settings=_cs)
@click.pass_context
def stop(ctx):
    """Stops the server."""
    cfg = get_configuration(cmd_args=ctx.args)

    if not servicer.is_alive(cfg.server):
        logger.warning('Server is not running... do nothing.')
    else:
        logger.info('Requesting server to stop.')
        client = servicer.connect(cfg.server)
        client.stop_server()


@cli.command(context_settings=_cs)
@click.pass_context
def log(ctx):
    """Log thermocouple readings to a file.

    The default output directory
    and filename are specified in the configuration file. Additional files
    may be specified as log targets.
    """
    cfg = get_configuration(cmd_args=ctx.args)
    if not servicer.is_alive(cfg.server):
        logger.warning('Server is not running!')
        return

    client = servicer.connect(cfg.server)
    with TCFileLogger(client, cfg.logging) as file:
        file.log_header()
        with file.start_logging_temperatures():
            try:
                while True:
                    time.sleep(1.0)
            except KeyboardInterrupt:
                logger.info('Stop logging.')


@cli.command(context_settings=_cs)
@click.pass_context
def ui(ctx):
    """Start the user interface to display thermocouple readings."""
    try:
        from tclogger_ui.__main__ import main

        del sys.argv[1]
        main()
    except Exception as e:
        logger.error('Could not start user interface.', exc_info=e)


if __name__ == '__main__':
    cli()
