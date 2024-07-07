# %%
import argparse
import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Event

from pymodbus import Framer, pymodbus_apply_logging_config
from pymodbus.client import ModbusTcpClient
from pymodbus.datastore import ModbusServerContext, ModbusSimulatorContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import ModbusTcpServer

# %%
demo_config = {
    "setup": {
        "co size": 100,
        "di size": 150,
        "hr size": 200,
        "ir size": 250,
        "shared blocks": True,
        "type exception": False,
        "defaults": {
            "value": {
                "bits": 0,
                "uint16": 0,
                "uint32": 0,
                "float32": 0.0,
                "string": "",
            },
            "action": {
                "bits": None,
                "uint16": None,
                "uint32": None,
                "float32": None,
                "string": None,
            },
        },
    },
    "invalid": [],
    "write": [],
    "bits": [],
    "uint16": [
        {
            "addr": 16,
            "value": 3124,
            "action": "random",
            "kwargs": {"minval": 0, "maxval": 12},
        },
        {"addr": [17, 18], "value": 5678},
        {"addr": [19, 20], "value": 14661, "action": "increment"},
    ],
    "uint32": [],
    "float32": [
        {"addr": [31, 32], "value": 3124.17},
        {"addr": [33, 36], "value": 5678.19},
        {"addr": [37, 40], "value": 345000.18, "action": "increment"},
    ],
    "string": [],
    "repeat": [],
}


# %%#
def main(cancel: Event):
    async def run():
        context = ModbusServerContext(
            slaves=ModbusSimulatorContext(demo_config, custom_actions=None), single=True
        )

        server = ModbusTcpServer(
            context, framer=Framer.SOCKET, address=('localhost', 5020)
        )
        await server.listen()

        while not cancel.is_set():
            pass

        await server.shutdown()

    asyncio.run(run())


pool = ThreadPoolExecutor()
cancel = Event()
future = pool.submit(main, cancel)

print('wait for start')
while not future.running():
    pass
print('started')

client = ModbusTcpClient('localhost', port=5020)
print(vars(client.read_holding_registers(16)))
print(vars(client.read_holding_registers(16)))

print('shutting down')
cancel.set()

future.cancel()
wait([future])
