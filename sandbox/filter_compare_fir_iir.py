from pylab import *
from scipy.signal.filter_design import ellip
from scipy.signal import remez, freqz, iirdesign
from scipy.signal.signaltools import lfilter

figure()

N = 2**16
fs = 44100.
x = arange(0,N)/fs
f = 18000.
#signal
y = sin(2*pi*x*f)

#window
Nw = 2**13
window = zeros(N)
window[:Nw] = hamming(Nw)

# windowed signal
y *= window

(b_iir, a_iir) = iirdesign(0.49, 0.51, 0.05, 70, analog=0, ftype='ellip', output='ba')
print "IIR coeff created", len(b_iir), len(a_iir)

Ntaps = 256
b_fir = remez(numtaps=Ntaps, bands=[0., 0.49/2., 0.51/2., 1./2.], desired=[1.,0.])#, maxiter=250, grid_density=64)
a_fir = [1.]
print "FIR coeff created", len(b_fir), len(a_fir)

yf_fir, zf = lfilter(b_fir, a_fir, y, zi=zeros(max(len(a_fir),len(b_fir))-1))

impulse = zeros(N); impulse[0] = 1.
yf_imp_fir, zf = lfilter(b_fir, a_fir, impulse, zi=zeros(max(len(a_fir),len(b_fir))-1))
yf_imp_iir, zf = lfilter(b_iir, a_iir, impulse, zi=zeros(max(len(a_iir),len(b_iir))-1))

clf()

subplot(311)
title("original and filtered signals")
plot(x, y)
plot(x, yf_fir)#; plot(x[-1]+x, yf2); plot(2*x[-1]+x, yf3)

subplot(312)
title("original and filtered frequency distributions")
semilogx(fftshift(fftfreq(N,1./fs))[N/2:], fftshift(20.*log(abs(fft(y))))[N/2:])
semilogx(fftshift(fftfreq(N,1./fs))[N/2:], fftshift(20.*log(abs(fft(yf_fir))))[N/2:])
ylim(ymin=1e-6)

#subplot(313); w, h = freqz(b, a, worN=N); loglog(w, abs(h)**2)
subplot(313)
title("filter impulse response")
semilogx(fftshift(fftfreq(N,1./fs))[N/2:], fftshift(20.*log(abs(fft(yf_imp_fir))))[N/2:])
semilogx(fftshift(fftfreq(N,1./fs))[N/2:], fftshift(20.*log(abs(fft(yf_imp_iir))))[N/2:])
show()