# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np

filename = "latency_log.txt"

data = np.loadtxt(filename)

plt.figure(1)
plt.hist(data, bins = 200)
plt.figure(2)
plt.plot(data)

plt.show()