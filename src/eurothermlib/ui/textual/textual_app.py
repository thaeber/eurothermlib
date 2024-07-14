from itertools import cycle
import logging

import reactivex as rx
from reactivex import operators as op
from reactivex.scheduler import ThreadPoolScheduler
from textual.app import App, ComposeResult
from textual.reactive import reactive, Reactive
from textual.widgets import Footer, Header

from eurothermlib.configuration import Config, get_configuration
from eurothermlib.server import connect
from eurothermlib.server.acquisition import TData

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

    def __init__(self, config: Config):
        super().__init__(watch_css=True)
        self.cfg = config
        self.client = connect(self.cfg)
        self.observable = rx.from_iterable(self.client.stream_process_values())

    def on_mount(self):
        self.observable.pipe(
            op.subscribe_on(thread_pool),
            # op.throttle_first(timedelta(seconds=1)),
            # op.filter(lambda data: data.deviceName == self.id),
        ).subscribe(self.update_readings)

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


def main():
    cfg = get_configuration()
    app = EurothermApp(cfg)
    app.run()


if __name__ == "__main__":
    main()
