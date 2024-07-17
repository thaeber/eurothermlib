from datetime import datetime
import pytest
from reactivex import operators as op

from eurothermlib.configuration import DeviceConfig
from eurothermlib.controllers import InstrumentStatus
from eurothermlib.server.acquisition import EurothermIO, TData, TemperatureRampState
from eurothermlib.server.proto import service_pb2
from eurothermlib.utils import TemperatureQ, DimensionlessQ
from google.protobuf.timestamp_pb2 import Timestamp


class TestTData:
    def test_to_grpc_response(self):
        now = datetime.now()
        data = TData(
            deviceName='test',
            timestamp=now,
            processValue=TemperatureQ(20.0, '°C'),
            setpoint=TemperatureQ(25.0, '°C'),
            workingSetpoint=TemperatureQ(30.0, '°C'),
            remoteSetpoint=TemperatureQ(25.0, '°C'),
            workingOutput=DimensionlessQ(1.2, '%'),
            status=InstrumentStatus.RemoteSPFail | InstrumentStatus.NewAlarm,
            rampStatus=TemperatureRampState.NoRamp,
        )

        response = data.to_grpc_response()
        assert response.deviceName == 'test'
        # assert response.timestamp == now
        assert response.processValue == 293.15
        assert response.setpoint == 298.15
        assert response.workingSetpoint == 303.15
        assert response.remoteSetpoint == 298.15
        assert response.workingOutput == 1.2
        assert response.status == int(
            InstrumentStatus.RemoteSPFail | InstrumentStatus.NewAlarm
        )
        assert response.rampStatus == int(TemperatureRampState.NoRamp)

    def test_from_grpc_response(self):
        now = datetime.now()

        timestamp = Timestamp()
        timestamp.FromDatetime(now)

        response = service_pb2.ProcessValues(
            deviceName='test',
            timestamp=timestamp,
            processValue=293.15,
            setpoint=298.15,
            workingSetpoint=303.15,
            workingOutput=1.2,
            status=int(InstrumentStatus.RemoteSPFail | InstrumentStatus.NewAlarm),
        )

        data = TData.from_grpc_response(response)
        assert data.deviceName == 'test'
        assert data.timestamp == now
        assert data.processValue == TemperatureQ(20.0, '°C')
        assert data.setpoint == TemperatureQ(25.0, '°C')
        assert data.workingSetpoint == TemperatureQ(30.0, '°C')
        assert data.workingOutput == DimensionlessQ(1.2, '%')
        assert data.status == InstrumentStatus.RemoteSPFail | InstrumentStatus.NewAlarm


class TestEurothermIO:
    @pytest.mark.slow
    def test_stream_values(self):
        cfg = [
            DeviceConfig(name='device1', sampling_rate='5Hz'),
            DeviceConfig(name='device2', sampling_rate='2Hz'),
        ]
        io = EurothermIO(cfg)

        io.start()

        data = []
        io.observable.pipe(
            op.take(10),
            op.do_action(data.append),
        ).run()
        assert len(data) == 10

        io.stop()
