from datetime import datetime
import pandas as pd
import pint
from eurothermlib.configuration import LoggingConfig
from eurothermlib.controllers.controller import InstrumentStatus
from eurothermlib.logging import FileDataLogger
from eurothermlib.server.acquisition import TData, TemperatureRampState


class TestFileDataLogger:
    def test_format_value(self):
        logger = FileDataLogger(LoggingConfig())

        assert logger._format_value(None, 'test') == 'test'
        assert (
            logger._format_value(None, datetime(2024, 7, 26, 10, 12, 32))
            == '2024-07-26T10:12:32'
        )
        assert logger._format_value(None, 2.123456789) == '2.12346'
        assert (
            logger._format_value('processValue', pint.Quantity(25.12345678, '°C'))
            == '298.273'
        )
        assert logger._format_value('workingOutput', pint.Quantity(0.8)) == '80'

    def test_format_line(self):
        logger = FileDataLogger(LoggingConfig())

        line = logger._format_line(
            dict(
                timestamp=datetime(2024, 7, 26, 10, 12, 32),
                processValue=pint.Quantity(25.12345678, '°C'),
                workingOutput=pint.Quantity(0.8),
                workingSetpoint=pint.Quantity(300, 'K'),
            )
        )

        assert line == '2024-07-26T10:12:32;298.273;80;300'

    def test_build_lines(self):
        logger = FileDataLogger(LoggingConfig())

        data = pd.DataFrame(
            [
                TData(
                    deviceName='reactor',
                    timestamp=datetime(2024, 7, 26, 10, 12, 32),
                    processValue=pint.Quantity(25.12345678, '°C'),
                    setpoint=pint.Quantity(310, 'K'),
                    workingSetpoint=pint.Quantity(300, 'K'),
                    remoteSetpoint=pint.Quantity(320.123456789, 'K'),
                    workingOutput=pint.Quantity(0.8),
                    status=InstrumentStatus.NewAlarm,
                    rampStatus=TemperatureRampState.NoRamp,
                ),
                TData(
                    deviceName='liner',
                    timestamp=datetime(2024, 7, 26, 10, 14, 32),
                    processValue=pint.Quantity(26.12345678, '°C'),
                    setpoint=pint.Quantity(310, 'K'),
                    workingSetpoint=pint.Quantity(300, 'K'),
                    remoteSetpoint=pint.Quantity(320.123456789, 'K'),
                    workingOutput=pint.Quantity(0.7),
                    status=InstrumentStatus.NewAlarm,
                    rampStatus=TemperatureRampState.NoRamp,
                ),
            ]
        )

        lines = list(logger._build_lines(data))

        assert lines == [
            '2024-07-26T10:12:32;298.273;80;300',
            '2024-07-26T10:14:32;299.273;70;300',
        ]
