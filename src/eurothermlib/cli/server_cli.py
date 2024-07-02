import logging
from concurrent import futures

import click

from ..server import server
from .cli import cli, get_configuration

logger = logging.getLogger(__name__)


# @cli.command(context_settings=_cs)
@cli.command()
@click.pass_context
def start(ctx):
    """Starts the server for acquiring thermocouple readings."""
    logger.info('Starting server')

    # cfg = get_configuration(cmd_args=ctx.args)
    cfg = get_configuration()
    if server.is_alive(cfg.server):
        logger.warning('Server is already running... do nothing.')
    else:
        future = server.serve(cfg)
        try:
            while True:
                _, not_done = futures.wait([future], timeout=2.0)
                if not not_done:
                    break
        except KeyboardInterrupt:
            logger.warning('Keyboard interrupt detected. Trying to stop server...')
            client = server.connect(cfg.server)
            client.stop_server()


# @cli.command(context_settings=_cs)
@cli.command()
@click.pass_context
def stop(ctx):
    """Stops the server."""
    cfg = get_configuration()

    if not server.is_alive(cfg.server):
        logger.warning('Server is not running... do nothing.')
    else:
        logger.info('Requesting server to stop.')
        client = server.connect(cfg.server)
        client.stop_server()
