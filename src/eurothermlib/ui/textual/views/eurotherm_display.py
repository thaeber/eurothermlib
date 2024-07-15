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
from .setpoint_display import SetpointDisplay

logger = logging.getLogger(__name__)

thread_pool = ThreadPoolScheduler()


class StatusLabel(Label):
    state = reactive(False)

    def watch_state(self, value: bool):
        if value:
            self.add_class('enabled')
        else:
            self.remove_class('enabled')


class StatusDisplay(Static):
    status = reactive(InstrumentStatus.Ok)

    def compose(self) -> ComposeResult:
        yield StatusLabel('OK', id='ok')
        yield StatusLabel('NewAlarm', id='alarm')
        yield StatusLabel('SensorBreak', id='sensorBreak')
        yield StatusLabel('RemoteSPFail', id='remoteSPFail')

    def watch_status(self, status: InstrumentStatus):
        self.query_one('#ok').state = status == InstrumentStatus.Ok
        self.query_one('#alarm').state = (
            status & InstrumentStatus.NewAlarm == InstrumentStatus.NewAlarm
        )
        self.query_one('#sensorBreak').state = (
            status & InstrumentStatus.SensorBreak == InstrumentStatus.SensorBreak
        )
        self.query_one('#remoteSPFail').state = (
            status & InstrumentStatus.RemoteSPFail == InstrumentStatus.RemoteSPFail
        )


class TemperatureDisplay(Digits):
    pass


class CurrentValuesDisplay(Static):

    units = reactive('K')
    values: reactive[TData | None] = reactive(None)

    def __init__(self, *args, **kwargs):
        self.device_name = kwargs.pop('device_name', '')
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Label(f'Device: {self.device_name}')
        yield TemperatureDisplay()
        yield DataTable()
        yield StatusDisplay()
        yield Button('Rest Alarms', id='button-reset-alarms')

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_column('name', width=8)
        table.add_column('---value---', width=15)
        # table.add_columns('name', '---value---')
        table.add_rows(
            [
                ('TG.SP', 'nan'),
                ('WRK.SP', 'nan'),
                ('WKG.OP', 'nan'),
                ('Status', 'error'),
            ]
        )
        table.cursor_type = 'row'
        table.show_header = False

    # def update_values(self, values: TData):
    #     self.values = values

    def watch_values(self, values: TData):
        self.update_display()

    def watch_units(self, units: str):
        self.update_display()

    def update_display(self):
        values = self.values
        if values is not None:
            # process value
            self.query_one(TemperatureDisplay).update(
                f'{values.processValue.to(self.units):.2f~#P}'
            )

            # self.query_one(TemperatureDisplay).value = (
            #     f'{values.processValue.to(self.units):.2f~#P}'
            # )

            # other values as table
            table = self.query_one(DataTable)

            styled = lambda s: Text(s, justify='right')
            table.update_cell_at(
                (0, 1), styled(f'{values.setpoint.to(self.units):.2f~#P}')
            )
            table.update_cell_at(
                (1, 1), styled(f'{values.workingSetpoint.to(self.units):.2f~#P}')
            )
            table.update_cell_at((2, 1), styled(f'{values.workingOutput:.2f~#P}'))
            table.update_cell_at((3, 1), styled(f'{values.status}'))

            # status
            self.query_one(StatusDisplay).status = values.status


class EurothermDisplay(Static):
    units = reactive('°C')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield CurrentValuesDisplay(device_name=self.id).data_bind(
                units=EurothermDisplay.units
            )
            with Collapsible(title='Setpoint', collapsed=False):
                yield SetpointDisplay().data_bind(units=EurothermDisplay.units)

    def update_values(self, values: TData):
        if values.deviceName == self.id:
            self.query_one(CurrentValuesDisplay).values = values
            self.query_one(SetpointDisplay).remoteSetpointEnabled = (
                InstrumentStatus.LocalRemoteSPSelect in values.status
            )
        else:
            logger.warn(
                'Received values with non-matching deviceName ({values.deviceName}) for EurothermDisplay with id {self.id}'
            )

    def on_mount(self):
        pass

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == 'button-enable':
            await self.run_action(f'app.enable_remote_setpoint("{self.id}")')
        elif event.button.id == 'button-disable':
            await self.run_action(f'app.disable_remote_setpoint("{self.id}")')
        elif event.button.id == 'button-reset-alarms':
            await self.run_action(f'app.acknowledge_alarms("{self.id}")')
