# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt
from scipy.signal.filter_design import iirdesign, tf2zpk
from scipy.signal.signaltools import lfilter, lfiltic
import numpy as np
from numpy.fft import fft, fftshift, fftfreq
import time

from friture_extensions.lfilter import pyx_lfilter_float64_1D

def pure_lfilter_float64_1D(b, a, x, zi):
    assert len(b.shape) == 1, "only 1D filters are allowed"
    assert b.shape == a.shape, "a and b must be of the same shape"
    assert len(zi.shape) == 1
    assert zi.shape == (b.shape[0]-1,)

    len_x = x.shape[0]
    len_b = b.shape[0]

    y = np.empty(x.shape)
    z = np.array(zi, copy=True)

    for k in range(len_x):
        if len_b > 1:
            y[k] = z[0] + b[0] * x[k] # Calculate first delay (output)

            # Fill in middle delays
            for n in range(len_b - 2):
                z[n] = z[1+n] + x[k] * b[1+n] - y[k] * a[1+n]

            # Calculate last delay
            z[len_b - 2] = x[k] * b[len_b - 1] - y[k] * a[len_b - 1]
        else:
            y[k] = x[k] * b[0]

    return y, z





N = 256*256#2**16
fs = 44100.
x = np.arange(0, N)/fs
f = 1800.

#signal
y = np.sin(2*np.pi*x*f)

#window
window = np.hanning(N)

# windowed signal
#y *= window

w1 = 0.49
w2 = 0.51
gpass = 0.05
gstop = 70.

#(b_full, a_full) = iirdesign(0.49, 0.51, 0.05, 70, analog=0, ftype='ellip', output='ba')
(b, a) = iirdesign(w1, w2, gpass, gstop, analog=0, ftype='ellip', output='ba')
#Nfilt = 13
#w = 0.5
#pbrip = 0.05
#sbatt = 70.
#(b_full, a_full) = iirfilter(Nfilt, w, pbrip, sbatt, analog=0, btype='lowpass', ftype='ellip', output='ba')
#print "IIR coeff created", len(b_full), len(a_full)

#print "b", b_full
#print "a", a_full

z = np.zeros(b.shape[0]-1)

impulse = np.zeros(N); impulse[N/2] = 1.

t0 = time.time()
yf_imp_lfilter, zf = lfilter(b, a, impulse, zi=z)#, zi=zeros(max(len(a_full),len(b_full))-1))
t1 = time.time()
print("scipy", t1-t0)

t0 = time.time()
yf_imp_handmade, zf = pure_lfilter_float64_1D(b, a, impulse, z)
t1 = time.time()
print("pure", t1-t0)

t0 = time.time()
yf_imp_pyx, zf_pyx = pyx_lfilter_float64_1D(b, a, impulse, z)
t1 = time.time()
print("cython", t1-t0)

N2 = 100
N3 = 100
y2 = np.zeros(N2)
y2[0] = 1.
zeros = np.zeros(N2)

t0 = time.time()
z = np.zeros(b.shape[0]-1)
for i in range(N3):
    if i == 0:
        yf_mult_lfilter, zf = lfilter(b, a, y2, zi=zf)
    else:
        yf_mult_lfiter, zf = lfilter(b, a, zeros, zi=zf)
t1 = time.time()
print("scipy", t1-t0)

t0 = time.time()
z = np.zeros(b.shape[0]-1)
for i in range(N3):
    if i == 0:
        yf_mult_pyx, zf = pyx_lfilter_float64_1D(b, a, y2, zf)
    else:
        yf_mult_pyx, zf = pyx_lfilter_float64_1D(b, a, zeros, zf)
t1 = time.time()
print("cython", t1-t0)


z = np.zeros(b.shape[0]-1)
yf_lfilter, zf = lfilter(b, a, y, zi=z)#, zi=zeros(max(len(a_full),len(b_full))-1))
yf_handmade, zf = pure_lfilter_float64_1D(b, a, y, z)
yf_pyx, zf_pyx = pyx_lfilter_float64_1D(b, a, y, z)

#print("Direct:", t1-t0, "Cascade:", t2-t1)

plt.figure()

plt.subplot(211)
plt.title("original and filtered signals")
plt.plot(x, impulse)
plt.plot(x, yf_imp_lfilter)
plt.plot(x, yf_imp_handmade)
plt.plot(x, yf_imp_pyx)

plt.subplot(212)
plt.title("original and filtered signals")
plt.plot(x, y)
plt.plot(x, yf_lfilter)
plt.plot(x, yf_handmade)
plt.plot(x, yf_pyx)

plt.show()



