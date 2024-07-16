from __future__ import annotations

import logging
from itertools import cycle

import reactivex as rx
from reactivex import operators as op
from reactivex.scheduler import ThreadPoolScheduler
from textual.app import App, ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Footer, Header

from eurothermlib.configuration import Config, get_configuration
from eurothermlib.controllers.controller import RemoteSetpointState
from eurothermlib.server import connect
from eurothermlib.server.acquisition import TData

from .views.error_screen import ErrorScreen
from .views.eurotherm_display import EurothermDisplay

logger = logging.getLogger(__name__)

thread_pool = ThreadPoolScheduler()

UNITS = cycle(['°C', 'K'])


class EurothermApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = 'textual_app.css'
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("u", "toggle_units", "Toggle units"),
    ]
    units = reactive(next(UNITS))

    class ConnectionLost(Message):
        def __init__(self, ex: Exception = None):
            self.ex = ex

    def __init__(self, config: Config):
        super().__init__(watch_css=True)
        self.cfg = config

    def connect_to_server(self):

        def on_error(ex: Exception = None):
            self.call_from_thread(
                self.handle_connection_lost, EurothermApp.ConnectionLost(ex)
            )

        self.client = connect(self.cfg)
        self.observable = rx.from_iterable(self.client.stream_process_values())
        self.observable.pipe(
            op.subscribe_on(thread_pool),
            # op.throttle_first(timedelta(seconds=1)),
            # op.filter(lambda data: data.deviceName == self.id),
        ).subscribe(
            self.update_readings,
            on_error=on_error,
            on_completed=on_error,
        )

    def on_mount(self):
        self.connect_to_server()

    def handle_connection_lost(self, event: EurothermApp.ConnectionLost):

        def check_result(reconnect: bool):
            if reconnect:
                self.connect_to_server()
            else:
                self.exit()

        self.push_screen(ErrorScreen(), check_result)

    def update_readings(self, values: TData):
        self.query_one(f'#{values.deviceName}').update_values(values)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        for device in self.cfg.devices:
            yield EurothermDisplay(id=device.name).data_bind(units=EurothermApp.units)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_toggle_units(self):
        self.units = next(UNITS)
        logger.info(f'Changing display units to: {self.units}')

    def action_enable_remote_setpoint(self, device: str):
        self.client.toggle_remote_setpoint(device, RemoteSetpointState.ENABLE)

    def action_disable_remote_setpoint(self, device: str):
        self.client.toggle_remote_setpoint(device, RemoteSetpointState.DISBALE)

    def action_acknowledge_alarms(self, device):
        self.client.acknowledge_all_alarms(device)


def main():
    cfg = get_configuration()
    app = EurothermApp(cfg)
    app.run()


if __name__ == "__main__":
    main()
