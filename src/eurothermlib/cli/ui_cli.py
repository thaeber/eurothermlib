import logging
from concurrent import futures

import click

from ..server import servicer
from .cli import cli, get_configuration
from ..ui.textual import EurothermApp

logger = logging.getLogger(__name__)


@cli.group(short_help='Start user interfaces')
def ui():
    """
    Start a command line or a graphical user interface
    to display process values. Multiple UIs may be started
    at the same time.
    """
    pass


@ui.command()
@click.pass_context
def textual(ctx):
    """Textual command line interface."""

    cfg = get_configuration()

    logger.info('Starting textual app')
    app = EurothermApp(cfg)
    app.run()
