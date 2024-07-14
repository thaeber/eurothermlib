from eurothermlib.controllers.generic import GenericAddress


class TestGenericAddress:
    def test_address_values(self):
        # ensure that we only write to the correct volatile address
        assert GenericAddress.RmSP == 26
