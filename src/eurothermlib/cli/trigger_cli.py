import logging
import time
from datetime import datetime
from enum import Enum
from typing import cast

import click
import grpc
import nidaqmx
import nidaqmx.constants
import nidaqmx.stream_writers
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


def state2str(state: bool) -> str:
    """Convert boolean state to string representation."""
    return 'high' if state else 'low'


def _send_trigger_pulse(channel: str, width: TimeQ = TimeQ(0.2, 's'), state: bool = True):  # type: ignore
    logger.info('Sending trigger signal')
    gate = width.m_as('s')
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(channel)
        logger.info(
            f'Setting digital output on {channel} to {state} [{state2str(state)}]'
        )
        task.write([state])
        time.sleep(gate)
        logger.info(f'Reset digital output on {channel}')
        task.write([not state])


def _set_digital_output(channel: str, state: bool):
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(channel)
        logger.info(
            f'Setting digital output on {channel} to {state} [{state2str(state)}]'
        )
        task.write([state])


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
                    _send_trigger_pulse(channel)
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
                        _send_trigger_pulse(channel)
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
    _channel = _lookup_trigger_alias(cfg, channel)
    logger.info(
        f'Setting digital to `on` (high level) on channel {channel} [{_channel}])'
    )
    _set_digital_output(_channel, True)


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
    _channel = _lookup_trigger_alias(cfg, channel)
    logger.info(
        f'Setting digital to `off` (low level) on channel {channel} [{_channel}])'
    )
    _set_digital_output(_channel, False)


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
@click.option(
    '--level',
    type=click.Choice(['high', 'low']),
    default='high',
    show_default=True,
    help='The (digital) level of the trigger pulse.',
)
def pulse(ctx: click.Context, device: str, channel: str, width: TimeQ, level: str):
    """Send a digital pulse using `nidaqmx`

    Examples:

    \b
    eurotherm pulse Dev1/port2/line0 --width 0.2s
    """
    cfg: Config = ctx.obj['config']
    _channel = _lookup_trigger_alias(cfg, channel)
    if level == 'high':
        _level = True
    else:
        _level = False
    logger.info(f'Sending trigger pulse on channel {channel} [{_channel}]')
    with nidaqmx.Task():
        _send_trigger_pulse(_channel, width, _level)


@trigger.command()
@click.pass_context
@device_option
@click.argument('channel')
@click.argument('frequency', type=float)
@click.option(
    '--width',
    type=str,
    default='0.2s',
    show_default=True,
    callback=validate_time,
    help='The width of the trigger pulse.',
)
def burst(ctx: click.Context, device: str, channel: str, width: TimeQ):
    """Send a burst of digital pulses using `nidaqmx`

    Examples:

    \b
    eurotherm burst dev1/port2/line0 --frequency 1/min --width 0.2s
    """
    cfg: Config = ctx.obj['config']
    _channel = _lookup_trigger_alias(cfg, channel)
    logger.info(f'Sending trigger pulse on channel {channel} [{_channel}]')

    # with nidaqmx.Task():
    #     _send_trigger(_channel, width)

    sample_rate = 2000  # samples per channel per second
    samples_per_frame = 1000  # Define an appropriate value for samples per frame
    frames_per_buffer = 10  # Define an appropriate value for frames per buffer
    NR_OF_CHANNELS = 1  # Define the number of channels (DO NOT CHANGE THIS)

    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(
            _channel, line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE
        )
        task.timing.cfg_samp_clk_timing(
            rate=sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS
        )
        task.out_stream.output_buf_size = (
            samples_per_frame * frames_per_buffer * NR_OF_CHANNELS
        )
        writer = nidaqmx.stream_writers.DigitalSingleChannelWriter(task.out_stream)

        def writing_task_callback(
            task_handle: int,
            event_type: nidaqmx.constants.EveryNSamplesEventType,
            num_samples: int,
            callback_data: object,
        ):
            """Called every time a defined amount of samples have been transferred from the device output
            buffer. Registered by calling `task.register_every_n_samples_transferred_from_buffer_event`
            (see `nidaqmx` documentation: https://nidaqmx-python.readthedocs.io/en/stable/task.html#nidaqmx.task.Task.register_every_n_samples_transferred_from_buffer_event).

            Args:
                task_handle (int): Task handle index
                event_type (nidaqmx.constants.EveryNSamplesEventType): TRANSFERRED_FROM_BUFFER
                num_samples (int): Number of samples written into the write buffer
                callback_data (object): User data
            """
            writer.write_many_sample(next(callback_data), timeout=10.0)

            # callback function must return 0 to prevent raising TypeError exception.
            return 0

        output_frame_generator = None
        for _ in range(frames_per_buffer):
            writer.write_many_sample_port_byte(
                next(output_frame_generator), timeout=1.0
            )

        task.register_every_n_samples_transferred_from_buffer_event(
            samples_per_frame,
            lambda *args: writing_task_callback(*args[:-1], output_frame_generator),
        )
