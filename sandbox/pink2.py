# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 14:45:48 2011

@author: timothee
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 14:43:13 2011

@author: timothee
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import mlab

from scipy import stats

def pink1d(n, rvs=stats.norm.rvs):
    k = min(int(np.floor(np.log(n)/np.log(2))), 12)
    pink = np.zeros((n,), np.float)
    m = 1
    for i in range(k):
        p = int(np.ceil(float(n) / m))
        pink += np.repeat(rvs(size=p), m,axis=0)[:n]
        m <<= 1

    return pink/k

T_sim = pink1d(2**18*4)

#PSD - 1 hour window
NFFT = int(1024*16*2)
s_sim, f_sim = mlab.psd(T_sim, NFFT=NFFT, Fs=44100., scale_by_freq=True)


plt.figure()

plt.loglog(f_sim, np.sqrt(s_sim), label='sim')
plt.grid(); plt.xlabel('Freq'); plt.title('Amplitude spectrum'); plt.legend()

plt.show()
