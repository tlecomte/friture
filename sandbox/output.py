# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 23:59:48 2011

@author: timothee
"""

import pyaudio
import numpy as np
from scipy import stats

SAMPLING_RATE = 44100
FRAMES_PER_BUFFER = 1024

time_s = 10.
t = np.arange(0, time_s, 1./float(SAMPLING_RATE))

def pinknoise(n, rvs=stats.norm.rvs):
    k = min(int(np.floor(np.log(n)/np.log(2))), 12)
    pink = np.zeros((n,), np.float)

    for m in 2**np.arange(k):
        p = int(np.ceil(float(n) / m))
        pink += np.repeat(rvs(size=p), m, axis=0)[:n]

    return pink/k

p = pyaudio.PyAudio()

# open stream
stream = p.open(format = pyaudio.paInt16,
                channels = 1,
                rate = SAMPLING_RATE,
                output = True)

# play
i = 0
imax = int(np.floor(t.max()*SAMPLING_RATE/FRAMES_PER_BUFFER))

for i in range(0, imax):
    # white noise
    floatdata = np.random.standard_normal(FRAMES_PER_BUFFER)
    # sinusoid
    ti = t[i*FRAMES_PER_BUFFER: (i+1)*FRAMES_PER_BUFFER]
    f = 440.
    floatdata = np.sin(2*np.pi*ti*f)
    #pink noise
    floatdata = pinknoise(FRAMES_PER_BUFFER)
    
    intdata = (floatdata*(2.**(16-1))).astype(np.int16)
    chardata = intdata.tostring()
    stream.write(chardata)

stream.close()
p.terminate()
