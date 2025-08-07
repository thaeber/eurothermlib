import logging
import time
from datetime import datetime
from typing import Literal, cast

import click
import cloup
import grpc
import nidaqmx
import nidaqmx.constants
import pint
from rich.progress import Progress
from cloup.constraints import (
    If,
    IsSet,
    require_all,
    accept_none,
    mutually_exclusive,
)

from eurothermlib.configuration import Config
from eurothermlib.utils import FractionQ, FrequencyQ, TimeQ

from ..server import servicer
from .cli import cli, device_option, validate_quantity

logger = logging.getLogger(__name__)


@cli.group()
def trigger():
    """Generate trigger signals."""
    pass


def _lookup_channel_alias(cfg: Config, name: str):
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


def _send_trigger_pulse(
    channel: str,
    width: TimeQ = TimeQ(0.2, 's'),
    state: bool | Literal['high', 'low'] = True,
):
    logger.info('Sending trigger signal')
    gate = width.m_as('s')
    if state == 'high':
        state = True
    elif state == 'low':
        state = False
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
@click.option(
    '--width',
    type=str,
    default='0.2s',
    show_default=True,
    callback=validate_quantity(TimeQ),
    help='The width of the trigger pulse.',
)
@click.option(
    '--level',
    type=click.Choice(['high', 'low']),
    default='high',
    show_default=True,
    help='The (digital) level of the trigger pulse.',
)
def every(
    ctx: click.Context,
    device: str,
    interval: str,
    channel: str,
    width: TimeQ,
    level: str,
):
    """Send a digital trigger signal using `nidaqmx` at given time or
    temperature intervals.

    Examples:

    \b
    eurotherm trigger every 10min Dev1/port2/line0
    eurotherm trigger every 10K Dev1/port2/line0
    """
    cfg: Config = ctx.obj['config']
    channel = _lookup_channel_alias(cfg, channel)

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
                    _send_trigger_pulse(channel, width, level)
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
                        _send_trigger_pulse(channel, width, level)
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
    _channel = _lookup_channel_alias(cfg, channel)
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
    _channel = _lookup_channel_alias(cfg, channel)
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
    callback=validate_quantity(TimeQ),
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
    _channel = _lookup_channel_alias(cfg, channel)
    logger.info(f'Sending trigger pulse on channel {channel} [{_channel}]')
    with nidaqmx.Task():
        _send_trigger_pulse(_channel, width, level)


@trigger.command()
@click.pass_context
@device_option
@click.argument('channel')
@cloup.option_group(
    'Frequency and Duty Cycle',
    cloup.option(
        '--frequency',
        type=str,
        default=None,
        show_default=True,
        callback=validate_quantity(FrequencyQ),
        help='The frequency of the pulse train.',
    ),
    cloup.option(
        '--duty-cycle',
        type=str,
        default='50%',
        show_default=True,
        callback=validate_quantity(FractionQ),
        help='The duty cycle of the pulse train.',
    ),
)
@cloup.option_group(
    'On/off time',
    cloup.option(
        '--on-time',
        type=str,
        default=None,
        show_default=True,
        callback=validate_quantity(TimeQ),
        help='The on time of the pulse train.',
    ),
    cloup.option(
        '--off-time',
        type=str,
        default=None,
        show_default=True,
        callback=validate_quantity(TimeQ),
        help='The off time of the pulse train.',
    ),
)
@cloup.constraint(If(~IsSet('frequency'), then=require_all), ['on_time', 'off_time'])
@cloup.constraint(If(IsSet('frequency'), then=accept_none), ['on_time', 'off_time'])
@cloup.option_group(
    'Duration',
    cloup.option(
        '--num-pulses',
        type=click.IntRange(min=1),
        default=None,
        show_default=True,
        help='The number of pulses to generate. If not set, the pulse train will run indefinitely.',
    ),
    cloup.option(
        '--timespan',
        type=str,
        default=None,
        show_default=True,
        callback=validate_quantity(TimeQ),
        help='The duration of the pulse train in seconds. If not set, the pulse train will run indefinitely.',
    ),
    constraint=mutually_exclusive,
)
@click.option(
    '--idle-state',
    type=click.Choice(['high', 'low']),
    default='low',
    show_default=True,
    help='Specifies the resting state of the output terminal.',
)
@click.option(
    '--initial-delay',
    type=str,
    default='0s',
    show_default=True,
    callback=validate_quantity(TimeQ),
    help='The amount of time in seconds to wait before generating the first pulse.',
)
def pulsetrain(
    ctx: click.Context,
    device: str,
    channel: str,
    frequency: FrequencyQ | None,
    duty_cycle: FractionQ,
    on_time: TimeQ | None,
    off_time: TimeQ | None,
    num_pulses: int | None,
    timespan: TimeQ | None,
    idle_state: Literal['high', 'low'],
    initial_delay: TimeQ,
):
    """
    Generate a continuous digital pulse train on the specified channel using NI-DAQmx.

    You can specify the pulse train by either:
      - Frequency and duty cycle (e.g. --frequency 1Hz --duty-cycle 50%)
      - On and off times (e.g. --on-time 0.5s --off-time 0.5s)

    The channel should be a programmable function input (PFI) line, such as `/dev1/pfi0`.
    Internally, counter `ctr0` is used to generate the pulses, and counter `ctr1` counts
    the number of pulses produced.

    Examples:

      eurotherm pulsetrain dev1/port2/line0 --frequency 1Hz
      eurotherm pulsetrain dev1/port2/line0 --on-time 0.5s --off-time 0.5s
    """
    cfg: Config = ctx.obj['config']

    # lookup the channel alias in the configuration
    _channel = _lookup_channel_alias(cfg, channel)

    # try to extract the NI device name from the channel
    if _channel.startswith('/'):
        ni_device = _channel.split('/')[1]
    else:
        ni_device = _channel.split('/')[0]

    # check duty cycle
    if not (0 < duty_cycle.m_as('') < 1):
        raise click.BadParameter(
            f'Duty cycle must be in the range (0%, 100%), got {duty_cycle.m_as("")}'
        )

    # check idle state
    if idle_state == 'low':
        _idle_state = nidaqmx.constants.Level.LOW
    elif idle_state == 'high':
        _idle_state = nidaqmx.constants.Level.HIGH
    else:
        raise click.BadParameter(
            f'Idle state must be either "high" or "low", got {idle_state}'
        )

    # generate the pulse train
    logger.info(f'Sending trigger burst on channel {channel} [{_channel}]')
    with nidaqmx.Task() as task, nidaqmx.Task() as task_input:
        if frequency is not None:
            logger.info(
                f'Generating pulse train with frequency {frequency:~P} and duty cycle {duty_cycle:~P}'
            )
            channel = task.co_channels.add_co_pulse_chan_freq(
                f'{ni_device}/ctr0',
                units=nidaqmx.constants.FrequencyUnits.HZ,
                freq=frequency.m_as('Hz'),
                idle_state=_idle_state,
                initial_delay=initial_delay.m_as('s'),
                duty_cycle=duty_cycle.m_as(''),
            )
        elif on_time is not None and off_time is not None:
            logger.info(
                f'Generating pulse train with on time {on_time:~P} and off time {off_time:~P}'
            )
            channel = task.co_channels.add_co_pulse_chan_time(
                f'{ni_device}/ctr0',
                units=nidaqmx.constants.TimeUnits.SECONDS,
                idle_state=_idle_state,
                initial_delay=initial_delay.m_as('s'),
                low_time=on_time.m_as('s'),
                high_time=off_time.m_as('s'),
            )
        channel.co_pulse_term = _channel
        task.timing.cfg_implicit_timing(
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS
        )

        channel = task_input.ci_channels.add_ci_count_edges_chan(
            f'{ni_device}/ctr1',
            edge=nidaqmx.constants.Edge.RISING,
            initial_count=0,
            count_direction=nidaqmx.constants.CountDirection.COUNT_UP,
        )
        channel.ci_count_edges_term = _channel

        task.start()
        task_input.start()
        t0 = datetime.now()
        try:
            edge_counts = 0
            _previous_edge_counts = 0
            while True:
                edge_counts = task_input.read()
                elapsed_time = (datetime.now() - t0).total_seconds()
                if (timespan is not None) and (elapsed_time > timespan.m_as('s')):
                    logger.info(
                        f'Timespan of {timespan:~P} reached with at total of {edge_counts} pulses.'
                    )
                    break
                elif edge_counts != _previous_edge_counts:
                    logger.info(
                        f'Generated {edge_counts:n} pulses in {elapsed_time:.2f} seconds'
                    )
                    if num_pulses is not None and edge_counts >= num_pulses:
                        logger.info(
                            f'Reached the specified number of pulses: {num_pulses:n}'
                        )
                        break
                    _previous_edge_counts = edge_counts

        except KeyboardInterrupt:
            pass
        finally:
            print(f"\nAcquired {edge_counts:n} total counts.")

            task_input.stop()
            task.stop()


# @trigger.command()
# @click.pass_context
# @device_option
# @click.argument('channel')
# # @click.argument('frequency', type=float)
# def burst(ctx: click.Context, device: str, channel: str):
#     """Send a burst of digital pulses using `nidaqmx`

#     Examples:

#     \b
#     eurotherm burst dev1/port2/line0 --frequency 1/min --width 0.2s
#     """
#     cfg: Config = ctx.obj['config']
#     _channel = _lookup_trigger_alias(cfg, channel)
#     logger.info(f'Sending trigger burst on channel {channel} [{_channel}]')

#     FRAME_PER_BUFFER = 4  # Define an appropriate value for frames per buffer
#     NR_OF_CHANNELS = 1  # Define the number of channels (DO NOT CHANGE THIS)

#     frequency = pint.Quantity(1, 'Hz')
#     period = 1.0 / frequency
#     duty_cycle = pint.Quantity(10, '%')
#     width = period * duty_cycle
#     print(frequency, period.to('s'), duty_cycle, width.to('s'))

#     resolution = pint.Quantity(10.0, 'ms')
#     sample_rate = (1.0 / resolution).m_as('Hz')  # samples per channel per second
#     samples_per_frame = int(
#         (period / resolution).m_as('')
#     )  # Define an appropriate value for samples per frame
#     print(sample_rate, samples_per_frame)

#     index = np.arange(samples_per_frame, dtype=np.uint32)
#     frame_data = np.where(
#         index < samples_per_frame * duty_cycle.m_as(''),
#         np.full_like(index, 16, dtype=np.uint32),
#         np.zeros_like(index, dtype=np.uint32),
#     )

#     with nidaqmx.Task() as task:
#         task.do_channels.add_do_chan(
#             _channel, line_grouping=nidaqmx.constants.LineGrouping.CHAN_FOR_ALL_LINES
#         )
#         task.timing.cfg_samp_clk_timing(
#             rate=sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS
#         )
#         task.out_stream.output_buf_size = (
#             samples_per_frame * FRAME_PER_BUFFER * NR_OF_CHANNELS
#         )
#         writer = nidaqmx.stream_writers.DigitalSingleChannelWriter(task.out_stream)

#         def writing_task_callback(
#             task_handle: int,
#             event_type: nidaqmx.constants.EveryNSamplesEventType,
#             num_samples: int,
#             callback_data: object,
#         ):
#             """Called every time a defined amount of samples have been transferred from the device output
#             buffer. Registered by calling `task.register_every_n_samples_transferred_from_buffer_event`
#             (see `nidaqmx` documentation: https://nidaqmx-python.readthedocs.io/en/stable/task.html#nidaqmx.task.Task.register_every_n_samples_transferred_from_buffer_event).

#             Args:
#                 task_handle (int): Task handle index
#                 event_type (nidaqmx.constants.EveryNSamplesEventType): TRANSFERRED_FROM_BUFFER
#                 num_samples (int): Number of samples written into the write buffer
#                 callback_data (object): User data
#             """
#             print(f'samples {num_samples}')
#             writer.write_many_sample_port_uint32(
#                 frame_data, timeout=nidaqmx.constants.WAIT_INFINITELY
#             )
#             print('written')

#             # callback function must return 0 to prevent raising TypeError exception.
#             return 0

#         for _ in range(FRAME_PER_BUFFER - 1):
#             writer.write_many_sample_port_uint32(frame_data, timeout=1.0)

#         task.register_every_n_samples_transferred_from_buffer_event(
#             samples_per_frame,
#             # lambda *args: writing_task_callback(*args[:-1], frame_data),
#             writing_task_callback,
#         )

#         task.start()

#         time.sleep(20.0)  # Keep the task running for a while
#         task.stop()
