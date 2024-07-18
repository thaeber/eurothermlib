from datetime import timedelta
import logging
import time

import click
import grpc
from rich.pretty import pretty_repr

from eurothermlib.configuration import Config
from eurothermlib.controllers.controller import InstrumentStatus
from eurothermlib.utils import TemperatureQ, TemperatureRateQ, TimeQ

from ..server import servicer
from .cli import (
    cli,
    device_option,
    validate_temperature,
    validate_temperature_rate,
    validate_time,
)
import reactivex as rx
import reactivex.operators as op

logger = logging.getLogger(__name__)


@cli.group()
def remote():
    """Enable/disable remote setpoint."""
    pass


@remote.command()
@click.pass_context
@device_option
def enable(ctx: click.Context, device: str):
    """Enable remote setpoint"""
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
@device_option
def disable(ctx: click.Context, device: str):
    """Disable remote setpoint"""
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


@remote.command(short_help='Set the remote setpoint')
@click.pass_context
@device_option
@click.argument('temperature', callback=validate_temperature)
def set(ctx: click.Context, temperature: TemperatureQ, device: str):
    """Set remote setpoint to the given TEMPERATURE.

    Examples:

    \b
    eurotherm remote set 50°C
    eurotherm remote set 330K
    eurotherm remote set "330 K"

    TEMPERATURE: New remote setpoint. Must consist of a value and
    a unit (without a space in between), e.g. 30°C, 30degC,
    313K, ... If a space is used between the value and unit,
    the entire expression must be enclosed in quotation marks,
    e.g. "313 K".
    """
    cfg: Config = ctx.obj['config']
    try:
        client = servicer.connect(cfg.server)
        client.is_alive()

        client.set_remote_setpoint(device, temperature)
    except grpc.RpcError as ex:
        logger.error('Remote RPC call failed.')
        logger.error(ex)


@remote.group()
def ramp():
    """Start/stop temeprature ramp"""
    pass


@ramp.command(short_help='Set the remote setpoint')
@click.pass_context
@device_option
@click.argument('temperature', callback=validate_temperature)
@click.option(
    '-r',
    '--rate',
    type=str,
    default='2 K/min',
    show_default=True,
    callback=validate_temperature_rate,
    help='The rate at which the temeprature will increase, e.g. 2K/min',
)
@click.option(
    '-i',
    '--interval',
    type=str,
    default='15s',
    show_default=True,
    callback=validate_time,
    help=(
        'The time interval at which the current ramp '
        'value is displayed/logged to reduce clutter '
        'on the log file.'
    ),
)
def start(
    ctx,
    temperature: TemperatureQ,
    rate: TemperatureRateQ,
    device: str,
    interval: TimeQ,
):
    """Starts a temperature ramp.

    The ramp starts from the current temperature with an
    optional rate (e.g., K/min) until the target TEMPERATURE
    is reached.

    Examples:

    \b
    eurotherm remote ramp start 50°C
    eurotherm remote ramp start 50°C --rate 2K/min

    TEMPERATURE: The target temperature. Must consist of a value and
    a unit (without a space in between), e.g. 30°C, 30degC,
    313K, ... If a space is used between the value and unit,
    the entire expression must be enclosed in quotation marks,
    e.g. "313 K".
    """
    cfg: Config = ctx.obj['config']
    try:
        client = servicer.connect(cfg.server)
        client.is_alive()

        last = time.monotonic()
        dt = interval.m_as('s')
        for T in client.start_temperature_ramp(device, temperature, rate):
            current = time.monotonic()
            if current - last >= dt:
                logger.info(f'Temperature: {T.to("°C"):.2f~P}')
                last = current

    except grpc.RpcError as ex:
        logger.error('Remote RPC call failed.')
        logger.error(ex)
