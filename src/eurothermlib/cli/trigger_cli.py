import logging
import time
from typing import cast
from datetime import datetime, timedelta

import click
import grpc
import nidaqmx
from rich.pretty import pretty_repr
from rich.progress import Progress
import pint

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

logger = logging.getLogger(__name__)


@cli.group()
def trigger():
    """Generate trigger signals."""
    pass


def _send_trigger(channel: str):
    logger.info('Sending trigger signal')
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(channel)
        task.write([True])
        time.sleep(0.2)
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
    eurotherm trigger every 10min
    eurotherm trigger every 10K
    """
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
        cfg: Config = ctx.obj['config']
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


# @trigger.command()
# @click.pass_context
# @device_option
# def enable(ctx: click.Context, device: str):
#     """Enable remote setpoint"""
#     cfg: Config = ctx.obj['config']
#     try:
#         client = servicer.connect(cfg.server)
#         client.is_alive()

#         client.toggle_remote_setpoint(device, servicer.RemoteSetpointState.ENABLE)

#         logger.info(f'[{repr(device)}] Checking remote setpoint status')
#         status = client.current_process_values(device).status
#         if InstrumentStatus.LocalRemoteSPSelect not in status:
#             logger.warning(f'[{repr(device)}] Could not enable remote setpoint')
#             logger.warning(f'[{repr(device)}] Instrument status: {pretty_repr(status)}')
#         else:
#             logger.info(f'[{repr(device)}] Remote setpoint successfully enabled')
#             logger.info(f'[{repr(device)}] Instrument status: {pretty_repr(status)}')

#     except grpc.RpcError as ex:
#         logger.error('Remote RPC call failed.')
#         logger.error(ex)
