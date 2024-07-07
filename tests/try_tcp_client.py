# %%
from pymodbus.client import ModbusTcpClient

# %%
client = ModbusTcpClient('localhost', port=5020)
# %%
vars(client.read_holding_registers(16))

# %%
vars(client.read_holding_registers(16))

# %%
