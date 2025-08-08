import functools
import logging
import os
import sys
from time import sleep
from typing import Type

import click
import cloup
import grpc
import pandas
import reactivex
from rich.pretty import pretty_repr
from rich.traceback import install

from eurothermlib.server import servicer
from eurothermlib.utils import TemperatureQ, TemperatureRateQ, TimeQ, TypedQuantity

from ..configuration import Config, get_configuration
from ..logging import AppLoggingMode, configure_app_logging

logger = logging.getLogger(__name__)

install(suppress=[click, reactivex, grpc, pandas])
os.environ["GRPC_VERBOSITY"] = "ERROR"

# configure logging
match sys.argv:
    case [_, 'ui', *rest]:
        configure_app_logging(AppLoggingMode.NONE)
    case [_, 'server', 'start']:
        configure_app_logging(AppLoggingMode.SERVER)
    case _:
        configure_app_logging(AppLoggingMode.CLIENT)


def get_command_name(ctx: click.Context):
    names = []
    while ctx is not None:
        names.insert(0, ctx.info_name)
        ctx = ctx.parent
    return '-'.join(names)


def validate_device(ctx: click.Context, param, value):
    cfg: Config = ctx.obj['config']

    if value is None:
        if len(cfg.devices) == 1:
            value = cfg.devices[0].name
            logger.info(f'Using [{repr(value)}] as default device.')
        else:
            msg = (
                'There is more than one device defined in the '
                'configuration. Unable to pick a default device.'
            )
            logger.error(msg)
            raise click.BadParameter(msg)

    if value not in [d.name for d in cfg.devices]:
        msg = f'Unknown device. The device [{repr(value)}] is not configured.'
        logger.error(msg)
        raise click.BadParameter(msg)

    return value


def device_option(f):
    @click.option(
        '-d',
        '--device',
        type=str,
        default=None,
        callback=validate_device,
        help='''The name of the device to which the command is applied.
            If only one device is configured, this device is used as the
            default. Otherwise, a device must be specified.''',
    )
    @functools.wraps(f)
    def wrapper_common_options(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper_common_options


def validate_time(ctx: click.Context, param, value):
    try:
        return TimeQ._validate(value)
    except ValueError as ex:
        logger.error(str(ex))
        raise click.BadParameter(
            f"units of {value} are incompatible with [temperature]."
        )


def validate_temperature(ctx: click.Context, param, value):
    try:
        return TemperatureQ._validate(value)
    except ValueError as ex:
        logger.error(str(ex))
        raise click.BadParameter(
            f"units of {value} are incompatible with [temperature]."
        )


def validate_temperature_rate(ctx: click.Context, param, value):
    try:
        return TemperatureRateQ._validate(value)
    except ValueError as ex:
        logger.error(str(ex))
        raise click.BadParameter(
            f"Units of {value} are incompatible with [temperature]/[time]."
        )


def validate_quantity(qtype: Type[TypedQuantity]):
    def wrapper(ctx: click.Context, param, value):
        if value is None:
            return None
        try:
            return qtype._validate(value)
        except ValueError as ex:
            logger.error(str(ex))
            raise click.BadParameter(
                f'Units of "{value}" are incompatible with expected units of '
                f'"{qtype.__dimensionality__}".'
            )

    return wrapper


@cloup.group()
@click.pass_context
@click.option(
    '-c',
    '--config',
    'config_filename',
    type=str,
    default='.eurotherm.yaml',
    show_default=True,
    help='''The name/path of the configuration file.''',
)
def cli(ctx: click.Context, config_filename: str):
    # load configuration
    config = get_configuration(filename=config_filename)
    # if config.app_logging is not None:
    #     logging.config.dictConfig(config.app_logging)

    # log original command
    logger.info(f'[cli] eurotherm {" ".join(sys.argv[1:])}')
    logger.info('Using configuration:')
    logger.debug(pretty_repr(config.model_dump()))

    ctx.obj = dict(config=config)


@cli.command()
@click.pass_context
def config(ctx):
    """Show configuration."""
    cfg: Config = ctx.obj['config']
    logger.info(pretty_repr(cfg))


@cli.command()
@click.pass_context
@device_option
@click.option(
    '-u',
    '--unit',
    default='°C',
    type=str,
    help='Display units of temperature values',
    show_default=True,
)
def current(ctx: click.Context, device: str, unit: str):
    """Return current process values.

    DEVICE (str): The name of the device for which the remote setpoint is enabled.
    """
    cfg: Config = ctx.obj['config']
    try:
        client = servicer.connect(cfg.server)
        client.is_alive()

        values = client.current_process_values(device)

        logger.info(f'deviceName={values.deviceName}')
        logger.info(f'timestamp={values.timestamp.isoformat()}')
        logger.info(f'processValue={values.processValue.to(unit):.2f~#P}')
        logger.info(f'setpoint={values.setpoint.to(unit):.2f~#P}')
        logger.info(f'workingSetpoint={values.workingSetpoint.to(unit):.2f~#P}')
        logger.info(f'remoteSetpoint={values.remoteSetpoint.to(unit):.2f~#P}')
        logger.info(f'workingOutput={values.workingOutput:.2f~#P}')
        logger.info(f'rampStatus={repr(values.rampStatus)}')
        logger.info(f'status={repr(values.status)}')
    except grpc.RpcError as ex:
        logger.error('Remote RPC call failed.')
        logger.error(ex)


@cli.command()
@click.pass_context
@click.argument('time', callback=validate_time)
@device_option
def hold(ctx: click.Context, time: TimeQ, device: str):
    """Hold device for a given TIME.

    TIME: The time to hold, e.g. 10min or 1h.
    """
    ctx.obj['config']
    try:
        # client = servicer.connect(cfg.server)
        # client.is_alive()

        logger.info(f'Waiting/holding for {time:~P} ...')
        sleep(time.m_as('s'))
        logger.info('..holding time ended')

    except grpc.RpcError as ex:
        logger.error('Remote RPC call failed.')
        logger.error(ex)


if __name__ == '__main__':
    cli()
