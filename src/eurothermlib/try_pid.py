# %%
import matplotlib.pyplot as plt
import numpy as np
import pint

from eurothermlib.pid import PID

ureg = pint.application_registry.get()
ureg.autoconvert_offset_to_baseunit = True


# %%
class ControlledSystem:
    def __init__(self):
        self.process_value = ureg.Quantity(20.0, 'degC').to('K')
        self.max_power = ureg.Quantity(600, 'W')
        self.RT = ureg.Quantity(20, 'degC')
        self.volume = ureg.Quantity(200 * 50 * 50, 'mm^3')
        self.heat_capacity = ureg.Quantity(3.756, 'J/cm^3/K')
        self.heat_loss = self.max_power / ureg.Quantity(480, 'K')

    def update(self, output, dt):
        power = output * self.max_power
        loss = (self.process_value - self.RT) * self.heat_loss
        energy = (power - loss) * dt
        delta_T = energy / (self.heat_capacity * self.volume)
        self.process_value += delta_T.to('K')
        return self.process_value.to('K')


# %%
system = ControlledSystem()
# system.process_value = ureg.Quantity(500, 'degC')
# system.update(1.0, ureg.Quantity(60.0, 's'))


pid = PID(1, 0.1, 0.05, setpoint=50.0)

# Assume we have a system we want to control in controlled_system
dt = ureg.Quantity(1.0, 's')
v = system.update(0.0, dt)

time = ureg.Quantity(0.0, 's')
data = []
while time < ureg('10min'):
    time += dt
    # Compute new output from the PID according to the systems current value
    control = pid(v.m_as('degC'), dt=dt.m_as('s'))

    # Feed the PID output to the system and get its current value
    v = system.update(control, dt)
    data.append([time.m_as('min'), v.m_as('degC')])
    # print(control, v.to('degC'))

plt.plot(*np.array(data).T)
# %%
