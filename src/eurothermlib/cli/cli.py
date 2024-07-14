import logging
import logging.handlers

import click
import grpc
import rich
from rich.pretty import pretty_repr
from rich.traceback import install

from eurothermlib.server import servicer

from ..configuration import Config, get_configuration

logger = logging.getLogger(__name__)

install()


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
@click.argument('device')
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
