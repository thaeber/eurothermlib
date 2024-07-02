import click
from rich.traceback import install

from ..configuration import Config, DeviceConfig

install()


def get_configuration():
    return Config(
        devices=[
            DeviceConfig(name='device1', sampling_rate='5Hz'),  # type: ignore
            DeviceConfig(name='device2', sampling_rate='2Hz'),  # type: ignore
        ]
    )


# def get_configuration(
#     cmd_args: Optional[List[str]] = None,
#     filename='./conf/tclogger.yaml',
#     use_cli=False,
# ):
#     try:
#         if Path(filename).exists():
#             cfg.merge_with(OmegaConf.load(filename))
#         if use_cli:
#             cfg.merge_with_cli()
#         if cmd_args is not None:
#             cfg.merge_with_dotlist(cmd_args)
#     except ConfigAttributeError as ex:
#         logger.critical("Invalid configuration option.", exc_info=ex)
#         raise ex

#     return cfg  # type: ignore


@click.group
def cli():
    pass
