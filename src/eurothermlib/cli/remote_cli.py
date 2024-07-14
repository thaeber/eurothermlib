import logging
from concurrent import futures
from rich.pretty import pretty_repr

import click

from eurothermlib.configuration import Config
from eurothermlib.controllers.controller import InstrumentStatus

from ..server import servicer
from .cli import cli, get_configuration
from ..ui.textual import EurothermApp
import grpc

logger = logging.getLogger(__name__)


@cli.group()
def remote():
    """Enable/disable remote setpoint."""
    pass


@remote.command()
@click.pass_context
@click.argument('device')
def enable(ctx: click.Context, device: str):
    """Enable usage of remote setpoint.

    DEVICE (str): The name of the device for which the remote setpoint is enabled.
    """
    cfg: Config = ctx.obj['config']
    try:
        client = servicer.connect(cfg.server)
        client.is_alive()

        client.toggle_remote_setpoint(device, servicer.RemoteSetpointState.ENABLE)

        logger.info(f'[{repr(device)}] Checking remote setpoint status')
        status = client.current_process_values(device).status
        if InstrumentStatus.LocalRemoteSPSelect not in status:
            logger.warning(f'[{repr(device)}] Could not enable remote setpoint')
            logger.warning(f'[{repr(device)}] Instrument status: {pretty_repr(status)}')
        else:
            logger.info(f'[{repr(device)}] Remote setpoint successfully enabled')
            logger.info(f'[{repr(device)}] Instrument status: {pretty_repr(status)}')

    except grpc.RpcError as ex:
        logger.error('Remote RPC call failed.')
        logger.error(ex)


@remote.command()
@click.pass_context
@click.argument('device')
def disable(ctx: click.Context, device: str):
    """Disable usage of remote setpoint.

    DEVICE (str): The name of the device for which the remote setpoint is disabled.
    """
    cfg: Config = ctx.obj['config']
    try:
        client = servicer.connect(cfg.server)
        client.is_alive()

        client.toggle_remote_setpoint(device, servicer.RemoteSetpointState.DISBALE)

        logger.info(f'[{repr(device)}] Checking remote setpoint status')
        status = client.current_process_values(device).status
        if InstrumentStatus.LocalRemoteSPSelect in status:
            logger.warning(f'[{repr(device)}] Could not disable remote setpoint')
            logger.warning(f'[{repr(device)}] Instrument status: {pretty_repr(status)}')
        else:
            logger.info(f'[{repr(device)}] Remote setpoint successfully disabled')
            logger.info(f'[{repr(device)}] Instrument status: {pretty_repr(status)}')

    except grpc.RpcError as ex:
        logger.error('Remote RPC call failed.')
        logger.error(ex)
