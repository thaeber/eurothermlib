import logging

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.validation import ValidationResult, Validator
from textual.widgets import Button, Input, Label, Static, Pretty


from eurothermlib.utils import TemperatureQ

logger = logging.getLogger(__name__)


class VariableLabel(Static):
    value = reactive('')

    def __init__(self, value: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value

    def render(self):
        return self.value


class SetpointDisplay(Static):
    units = reactive('°C')
    remoteSetpointEnabled = reactive(False)
    setpoint = reactive(TemperatureQ(25, '°C'), layout=True, init=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Button('Enable', id='button-enable')
                yield Button('Disable', id='button-disable')
                with Horizontal(id='status-group'):
                    yield Label('Remote select:', id='label-remote-select')
                    yield Label('disabled', id='label-disabled')
                    yield Label('enabled', id='label-enabled')
            with Horizontal():
                yield Label('Setpoint')
                yield Input(
                    value=f'{self.setpoint:~P}',
                    placeholder='e.g. 50°C',
                    id='input-setpoint',
                    validators=[TemperatureValidator()],
                )
                yield VariableLabel(f'{self.setpoint:~P}', id='setpoint-label')
                yield Static(classes='spacer')
                yield Button('Set', id='button-setpoint')
            yield Pretty([])

    def on_mount(self):
        pass

    def watch_units(self, units: str):
        self.query_one(
            '#setpoint-label', VariableLabel
        ).value = f'{self.setpoint.to(units):~P}'

    def watch_remoteSetpointEnabled(self, enabled: bool):
        if enabled:
            self.add_class('enabled')
        else:
            self.remove_class('enabled')

    # async def on_button_pressed(self, event: Button.Pressed):
    #     if event.button.id == 'button-setpoint':
    #         value = self.query_one('#input-setpoint', Input).value
    #         await self.run_action(
    #             f'app.set_remote_setpoint("{self.id}", "{value} {self.units}")'
    #         )

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        if not event.validation_result.is_valid:
            self.query_one(Pretty).update(event.validation_result.failure_descriptions)
            self.query_one('#setpoint-label', VariableLabel).add_class('error')
            self.query_one('#button-setpoint', Button).disabled = True
        else:
            self.query_one(Pretty).update([])
            self.setpoint = TemperatureQ._validate(event.value).to(self.units)
            self.query_one('#setpoint-label', VariableLabel).remove_class('error')
            self.query_one('#button-setpoint', Button).disabled = False

    def watch_setpoint(self, value: TemperatureQ):
        self.query_one(
            '#setpoint-label', VariableLabel
        ).value = f'{value.to(self.units):~P}'


class TemperatureValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        try:
            value = TemperatureQ._validate(value)
            return self.success()
        except Exception as ex:
            return self.failure(str(ex))
