import pint

from eurothermlib.controller import EurothermSimulator


class TestEurothermSimulator:
    def test_instantiation(self):
        controller = EurothermSimulator()
        assert controller.process_value == pint.Quantity(20, 'degC')
        assert controller.measured_value == pint.Quantity(0.8192, 'mV')
