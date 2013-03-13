import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, '.')

import friture.qsynthmeter as meter

scale = meter.IECScale()

x = np.linspace(-100, 10, 1000)
y = [scale.iec_scale(x0) for x0 in x]

plt.figure()
plt.plot(x, y)

plt.show()
