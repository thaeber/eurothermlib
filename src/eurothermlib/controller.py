import abc

from serial import Serial


class EurothermController(abc.ABC):
    @abc.abstractmethod
    def get_process_value(self):
        pass


class EurothermSimulator(EurothermController):
    def __init__(self):
        self.current_value = 20.0
        self.set_point = 30.0


class EurothermModel3208(EurothermController):
    def __init__(self, port: Serial):
        pass
