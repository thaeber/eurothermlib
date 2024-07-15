import logging
from typing import List

from reactivex.scheduler import ThreadPoolScheduler
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Checkbox,
    DataTable,
    Digits,
    Label,
    OptionList,
    Select,
    Static,
    Button,
    Collapsible,
)

from eurothermlib.controllers import InstrumentStatus
from eurothermlib.server.acquisition import TData

logger = logging.getLogger(__name__)


class SetpointDisplay(Static):
    units = reactive('°C')
    remoteSetpointEnabled = reactive(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Button('Enable', id='button-enable')
            yield Button('Disable', id='button-disable')
            with Horizontal(id='status-group'):
                yield Label('Remote select:')
                yield Label('disabled', id='label-disabled')
                yield Label('enabled', id='label-enabled')

    def on_mount(self):
        pass

    def watch_units(self, units: str):
        pass

    def watch_remoteSetpointEnabled(self, enabled: bool):
        if enabled:
            self.add_class('enabled')
        else:
            self.remove_class('enabled')
