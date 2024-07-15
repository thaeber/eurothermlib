import functools
import logging
import logging.handlers
import textwrap

import click
import grpc
from pint import DimensionalityError
from rich.pretty import pretty_repr
from rich.traceback import install

from eurothermlib.server import servicer
from eurothermlib.utils import TemperatureQ

from ..configuration import Config, get_configuration

logger = logging.getLogger(__name__)

install()


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
        help='''The name of the device to which the command is applied. If only one device 
            is configured, this device is used as the default. Otherwise, a device
            must be specified.''',
    )
    @functools.wraps(f)
    def wrapper_common_options(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper_common_options


def validate_temperature(ctx: click.Context, param, value):
    try:
        return TemperatureQ._validate(value)
    except ValueError as ex:
        logger.error(str(ex))
        raise click.BadParameter(f"Could not convert {value} to a temperature.")


@click.group
@click.pass_context
def cli(ctx: click.Context):
    config = get_configuration()
    if config.app_logging is not None:
        logging.config.dictConfig(config.app_logging)
    logging.debug('Using configuration:')
    logging.debug(pretty_repr(config.model_dump()))

    ctx.obj = dict(config=config)


@cli.command()
@click.pass_context
@device_option
def current(ctx: click.Context, device: str):
    """Return current process values.

    DEVICE (str): The name of the device for which the remote setpoint is enabled.
    """
    cfg: Config = ctx.obj['config']
    try:
        client = servicer.connect(cfg.server)
        client.is_alive()

        logger.info(f'[{repr(device)}] Reading process values')
        values = client.current_process_values(device)

        logger.info(f'deviceName={values.deviceName}')
        logger.info(f'timestamp={values.timestamp.isoformat()}')
        logger.info(f'processValue={values.processValue:.2f~#P}')
        logger.info(f'setpoint={values.setpoint:.2f~#P}')
        logger.info(f'workingSetpoint={values.workingSetpoint:.2f~#P}')
        logger.info(f'workingOutput={values.workingOutput:.2f~#P}')
        logger.info(f'status={repr(values.status)}')
    except grpc.RpcError as ex:
        logger.error('Remote RPC call failed.')
        logger.error(ex)


if __name__ == '__main__':
    cli()
