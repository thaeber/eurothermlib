import logging
import time
from datetime import datetime

import click
import grpc
from rich.progress import Progress
from eurothermlib.utils import TemperatureQ, TimeQ

from eurothermlib.configuration import Config

from ..server import servicer
from .cli import (
    cli,
    device_option,
)

logger = logging.getLogger(__name__)


@cli.group()
def wait():
    """Wait for timespan or until a temperature is reached."""
    pass


def validate_time(ctx: click.Context, param, value):
    try:
        return TimeQ._validate(value)
    except ValueError as ex:
        logger.error(str(ex))
        raise click.BadParameter(f"units of {value} are incompatible with [time].")


def validate_temperature(ctx: click.Context, param, value):
    try:
        return TemperatureQ._validate(value)
    except ValueError as ex:
        logger.error(str(ex))
        raise click.BadParameter(
            f"units of {value} are incompatible with [temperature]."
        )


@wait.command()
@click.pass_context
@click.argument('duration', callback=validate_time)
@device_option
def duration(ctx: click.Context, duration: TimeQ, device: str):
    """Hold device for a given DURATION.

    DURATION: The time to hold, e.g. 10min or 1h.
    """
    ctx.obj['config']
    try:
        # client = servicer.connect(cfg.server)
        # client.is_alive()

        logger.info(f'Waiting/holding for {duration:~P} ...')
        # time.sleep(time.m_as('s'))

        time_interval = duration.m_as('s')
        sleep_seconds = min(1.0, time_interval / 20)
        t0 = datetime.now()
        with Progress() as progress:
            task = progress.add_task('Waiting...', total=1.0, completed=0.0)
            while True:
                time.sleep(sleep_seconds)
                now = datetime.now()
                dt = (now - t0).total_seconds()
                progress.update(task, completed=dt / time_interval)
                if dt > time_interval:
                    # stop waiting
                    break

        logger.info('..holding time ended')

    except grpc.RpcError as ex:
        logger.error('Remote RPC call failed.')
        logger.error(ex)


@wait.command()
@click.pass_context
@device_option
@click.argument('temperature', callback=validate_temperature)
@click.option(
    '--tolerance',
    type=str,
    default='0.5K',
    show_default=True,
    callback=validate_temperature,
    help='The allowed difference between target and current temperature.',
)
def reach(
    ctx: click.Context, temperature: TemperatureQ, tolerance: TemperatureQ, device: str
):
    """Wait until given TEMPERATURE is reached.

    TEMPERATURE: The target temperature to wait for, e.g. 300K or 250degC.
    """
    cfg: Config = ctx.obj['config']
    try:
        # client = servicer.connect(cfg.server)
        # client.is_alive()

        logger.info(f'Waiting until {temperature:~P} is reached ...')
        # time.sleep(time.m_as('s'))

        client = servicer.connect(cfg.server)
        client.is_alive()

        T0 = client.current_process_values(device).processValue
        initial_dT = abs(temperature - T0)
        with Progress() as progress:
            task = progress.add_task('Waiting...', total=1.0, completed=0.0)
            for data in client.stream_process_values():
                if data.deviceName != device:
                    continue
                dT = abs(temperature - data.processValue)
                progress.update(task, completed=1.0 - dT / initial_dT)
                if dT < tolerance:
                    # temperature reached
                    break

        logger.info('...temperature reached')

    except grpc.RpcError as ex:
        logger.error('Remote RPC call failed.')
        logger.error(ex)
