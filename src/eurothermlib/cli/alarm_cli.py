import logging

import click
import grpc

from eurothermlib.configuration import Config

from ..server import servicer
from .cli import cli, device_option

logger = logging.getLogger(__name__)


@cli.group()
def alarm():
    """Acknowledge/read alarm status."""
    pass


@alarm.command()
@click.pass_context
@device_option
def ack(ctx: click.Context, device: str):
    """Acknowledge all alarms on the specified device.

    DEVICE (str): The name of the device for which the remote setpoint is enabled.
    """
    cfg: Config = ctx.obj['config']
    try:
        client = servicer.connect(cfg.server)
        client.is_alive()

        client.acknowledge_all_alarms(device)

    except grpc.RpcError as ex:
        logger.error('Remote RPC call failed.')
        logger.error(ex)
