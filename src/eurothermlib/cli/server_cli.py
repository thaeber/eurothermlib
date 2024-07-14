import logging
from concurrent import futures

import click

from ..server import servicer
from .cli import cli, get_configuration

logger = logging.getLogger(__name__)


@cli.group()
def server():
    """Starting/stopping the server used to interact with the devices."""
    pass


# @cli.command(context_settings=_cs)
@server.command()
@click.pass_context
def start(ctx):
    """Starts the server for acquiring thermocouple readings."""
    logger.info('Starting server')

    # cfg = get_configuration(cmd_args=ctx.args)
    cfg = get_configuration()
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


# @cli.command(context_settings=_cs)
@server.command()
@click.pass_context
def stop(ctx):
    """Stops the server."""
    cfg = get_configuration()

    if not servicer.is_alive(cfg.server):
        logger.warning('Server is not running... do nothing.')
    else:
        logger.info('Requesting server to stop.')
        client = servicer.connect(cfg.server)
        client.stop_server()
