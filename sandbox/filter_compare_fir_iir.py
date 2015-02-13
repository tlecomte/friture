from matplotlib import pylab as plt
import numpy as np
from scipy.signal.filter_design import iirdesign
from scipy.signal.fir_filter_design import remez
from scipy.signal.signaltools import lfilter
from numpy.fft import fft, fftshift, fftfreq

N = 2**13
fs = 44100.
x = np.arange(0,N)/fs
f = 1800.
#signal
y = np.sin(2*np.pi*x*f)

#window
window = np.hanning(N)

# windowed signal
y *= window

(b_iir, a_iir) = iirdesign(0.49, 0.51, 0.05, 70, analog=0, ftype='ellip', output='ba')
print("IIR coeff created", len(b_iir), len(a_iir))

Ntaps = 512
b_fir = remez(numtaps=Ntaps, bands=[0., 0.49/2., 0.51/2., 1./2.], desired=[1.,0.])#, maxiter=250, grid_density=64)
a_fir = [1.]
print("FIR coeff created", len(b_fir), len(a_fir))

import time
t0 = time.time()
yf_fir, zf = lfilter(b_fir, a_fir, y, zi=np.zeros(max(len(a_fir),len(b_fir))-1))
t1 = time.time()
yf_iir, zf = lfilter(b_iir, a_iir, y, zi=np.zeros(max(len(a_iir),len(b_iir))-1))
t2 = time.time()
tfir = t1 - t0
tiir = t2 - t1
print("fir", tfir, "iir", tiir, "fir/iir", tfir/tiir)

impulse = np.zeros(N); impulse[N/2] = 1.
yf_imp_fir, zf = lfilter(b_fir, a_fir, impulse, zi=np.zeros(max(len(a_fir),len(b_fir))-1))
yf_imp_iir, zf = lfilter(b_iir, a_iir, impulse, zi=np.zeros(max(len(a_iir),len(b_iir))-1))

plt.figure()

plt.subplot(411)
plt.title("original and filtered signals")
plt.plot(x, y)
plt.plot(x, yf_fir)
plt.plot(x, yf_iir)

plt.subplot(412)
plt.title("original and filtered frequency distributions")
freqScale = fftshift(fftfreq(N,1./fs))[N/2:]
plt.semilogx(freqScale, fftshift(20. * np.log10(abs(fft(y*window))))[N/2:])
plt.semilogx(freqScale, fftshift(20. * np.log10(abs(fft(yf_fir*window))))[N/2:])
plt.semilogx(freqScale, fftshift(20. * np.log10(abs(fft(yf_iir*window))))[N/2:])

plt.subplot(413)
plt.title("filter impulse magnitude response")
plt.semilogx(freqScale, fftshift(20. * np.log10(abs(fft(impulse*window))))[N/2:], label="signal")
plt.semilogx(freqScale, fftshift(20. * np.log10(abs(fft(yf_imp_fir*window))))[N/2:], label="FIR filt.")
plt.semilogx(freqScale, fftshift(20. * np.log10(abs(fft(yf_imp_iir*window))))[N/2:], label="IIR filt.")
plt.legend(loc='lower left')

plt.subplot(414)
plt.title("filter impulse phase response")
plt.semilogx(freqScale, fftshift(np.angle(fft(impulse*window)))[N/2:], label="signal")
plt.semilogx(freqScale, fftshift(np.angle(fft(yf_imp_fir*window)))[N/2:], label="FIR filt.")
plt.semilogx(freqScale, fftshift(np.angle(fft(yf_imp_iir*window)))[N/2:], label="IIR filt.")
plt.legend(loc='lower left')

plt.show()
