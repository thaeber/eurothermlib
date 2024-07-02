import pytest
from reactivex import operators as op

from eurothermlib.configuration import DeviceConfig
from eurothermlib.server.acquisition import EurothermIO


class TestEurothermIO:

    @pytest.mark.skip('Skipped long running server test')
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
