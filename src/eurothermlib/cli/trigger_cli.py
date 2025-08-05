import logging
import time
from datetime import datetime
from typing import cast

import click
import grpc
import nidaqmx
import pint
from rich.progress import Progress

from eurothermlib.configuration import Config
from eurothermlib.utils import TimeQ

from ..server import servicer
from .cli import cli, device_option, validate_time

logger = logging.getLogger(__name__)


@cli.group()
def trigger():
    """Generate trigger signals."""
    pass


def _lookup_trigger_alias(cfg: Config, name: str):
    """Lookup trigger alias in the configuration file."""
    for trigger in cfg.trigger:
        if trigger.name == name:
            logger.info(
                f'Found trigger {name} in configuration file with channel '
                f'{trigger.channel}'
            )
            return trigger.channel
    return name


def _send_trigger(channel: str, width: TimeQ = TimeQ(0.2, 's')):  # type: ignore
    logger.info('Sending trigger signal')
    gate = width.m_as('s')
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(channel)
        task.write([True])
        time.sleep(gate)
        task.write([False])


@trigger.command()
@click.pass_context
@device_option
@click.argument('interval')
@click.argument('channel')
def every(ctx: click.Context, device: str, interval: str, channel: str):
    """Send a digital trigger signal using `nidaqmx` at given time or
    temperature intervals.

    Examples:

    \b
    eurotherm trigger every 10min Dev1/port2/line0
    eurotherm trigger every 10K Dev1/port2/line0
    """
    cfg: Config = ctx.obj['config']
    channel = _lookup_trigger_alias(cfg, channel)

    ureg = pint.application_registry.get()
    intervalQ = ureg.Quantity(interval)
    intervalQ = cast(pint.Quantity, intervalQ)
    if intervalQ.check('[time]'):
        time_interval = intervalQ.m_as('s')
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
                    # send trigger signal
                    _send_trigger(channel)
                    # update t0
                    t0 = now
    elif intervalQ.check('[temperature]'):
        try:
            client = servicer.connect(cfg.server)
            client.is_alive()

            temperature_interval = intervalQ.to('K')
            T0 = client.current_process_values(device).processValue
            with Progress() as progress:
                task = progress.add_task('Waiting...', total=1.0, completed=0.0)
                for data in client.stream_process_values():
                    if data.deviceName != device:
                        continue
                    dT = abs(data.processValue - T0)
                    progress.update(task, completed=dT / temperature_interval)
                    if dT > temperature_interval:
                        # send trigger signal
                        _send_trigger(channel)
                        # update T0
                        T0 = data.processValue

        except grpc.RpcError as ex:
            logger.error('Remote RPC call failed.')
            logger.error(ex)
    else:
        logger.error('Interval must have dimensions of [time] or [temperature]')


@trigger.command()
@click.pass_context
@device_option
@click.argument('channel')
def on(ctx: click.Context, device: str, channel: str):
    """Set a digital signal to `on` (high level) using `nidaqmx`

    Examples:

    \b
    eurotherm trigger on Dev1/port2/line0
    """
    cfg: Config = ctx.obj['config']
    channel = _lookup_trigger_alias(cfg, channel)
    logger.info(f'Setting digital line to `on` (high level) on channel {channel})')
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(channel)
        task.write([True])


@trigger.command()
@click.pass_context
@device_option
@click.argument('channel')
def off(ctx: click.Context, device: str, channel: str):
    """Set a digital signal to `off` (low level) using `nidaqmx`

    Examples:

    \b
    eurotherm trigger on Dev1/port2/line0
    """
    cfg: Config = ctx.obj['config']
    channel = _lookup_trigger_alias(cfg, channel)
    logger.info(f'Setting digital line to `off` (low level) on channel {channel})')
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(channel)
        task.write([False])


@trigger.command()
@click.pass_context
@device_option
@click.argument('channel')
@click.option(
    '--width',
    type=str,
    default='0.2s',
    show_default=True,
    callback=validate_time,
    help='The width of the trigger pulse.',
)
def pulse(ctx: click.Context, device: str, channel: str, width: TimeQ):
    """Send a digital pulse using `nidaqmx`

    Examples:

    \b
    eurotherm pulse Dev1/port2/line0 --width 0.2s
    """
    cfg: Config = ctx.obj['config']
    channel = _lookup_trigger_alias(cfg, channel)
    logger.info(f'Sending trigger pulse on channel {channel})')
    with nidaqmx.Task():
        _send_trigger(channel, width)
