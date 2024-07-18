import logging

from reactivex.scheduler import ThreadPoolScheduler
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import (
    DataTable,
    Digits,
    Label,
    Static,
    Button,
    Collapsible,
)
from textual.widget import Widget

from eurothermlib.controllers import InstrumentStatus
from eurothermlib.server.acquisition import TData, TemperatureRampState
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
        yield StatusLabel('New Alarm', id='alarm')
        yield StatusLabel('Sensor Break', id='sensorBreak')
        yield StatusLabel('Remote SP Fail', id='remoteSPFail')
        yield StatusLabel('')
        yield StatusLabel('Using Remote SP', id='useRemoteSP')

    def watch_status(self, status: InstrumentStatus):
        self.query_one('#ok').state = InstrumentStatus.Ok in status
        self.query_one('#alarm').state = InstrumentStatus.NewAlarm in status
        self.query_one('#sensorBreak').state = InstrumentStatus.SensorBreak in status
        self.query_one('#remoteSPFail').state = InstrumentStatus.RemoteSPFail in status
        self.query_one('#useRemoteSP').state = (
            InstrumentStatus.LocalRemoteSPSelect in status
        )


class RampStatusLabel(Widget):

    status = reactive(TemperatureRampState.NoRamp)

    def render(self):
        label = 'No Ramp'

        match self.status:
            case TemperatureRampState.Running:
                label = 'Running'
            case TemperatureRampState.Stopped:
                label = 'Stopped'
            case TemperatureRampState.Finished:
                label = 'Finished'

        return label

    def watch_status(self, status: TemperatureRampState):
        self.remove_class('running', 'stopped', 'finished')
        match status:
            case TemperatureRampState.Running:
                self.add_class('running')
            case TemperatureRampState.Stopped:
                self.add_class('stopped')
            case TemperatureRampState.Finished:
                self.add_class('finished')


class TemperatureDisplay(Digits):
    pass


class CurrentValuesDisplay(Static):
    units = reactive('K')
    values: reactive[TData | None] = reactive(None)

    def __init__(self, *args, **kwargs):
        self.device_name = kwargs.pop('device_name', '')
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(f'Device: {self.device_name}')
            yield Label(' ', id='acquire')
        yield TemperatureDisplay()
        yield DataTable()
        with Horizontal():
            yield Label('Remote ramp:')
            yield RampStatusLabel()
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
                ('Rm.SP', 'nan'),
                ('WKG.OP', 'nan'),
                ('Status', 'error'),
            ]
        )
        table.cursor_type = 'none'
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
            self.query_one('#acquire').toggle_class('on')

            # process value
            self.query_one(TemperatureDisplay).update(
                f'{values.processValue.to(self.units):.2f~#P}'
            )

            # self.query_one(TemperatureDisplay).value = (
            #     f'{values.processValue.to(self.units):.2f~#P}'
            # )

            # other values as table
            table = self.query_one(DataTable)

            def styled(s):
                return Text(s, justify='right')

            table.update_cell_at(
                (0, 1), styled(f'{values.setpoint.to(self.units):.2f~#P}')
            )
            table.update_cell_at(
                (1, 1), styled(f'{values.workingSetpoint.to(self.units):.2f~#P}')
            )
            table.update_cell_at(
                (2, 1), styled(f'{values.remoteSetpoint.to(self.units):.2f~#P}')
            )
            table.update_cell_at((3, 1), styled(f'{values.workingOutput:.2f~#P}'))
            table.update_cell_at((4, 1), styled(f'{values.status}'))

            # status
            self.query_one(StatusDisplay).status = values.status
            self.query_one(RampStatusLabel).status = values.rampStatus


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
                (
                    f'Received values with non-matching deviceName '
                    f'({values.deviceName}) for EurothermDisplay with '
                    f'id {self.id}'
                )
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
