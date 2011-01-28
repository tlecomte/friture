from pylab import *
from scipy.signal.filter_design import ellip
from scipy.signal import remez, freqz
from scipy.signal.signaltools import lfilter

figure()
N = 2**16
fs = 44100.
x = arange(0,N)/fs
f = 63.4

Nw = 2**13
window = zeros(N)
window[:Nw] = hamming(Nw)
y = window*sin(2*pi*x*f)
pbrip = .5
sbrip = 50
order = 2
fi = 63.41
flow = 62.5
fhigh = 64.33
wi = fi/(fs/2.)
wlow = flow/(fs/2.)
whigh = fhigh/(fs/2.)
w = [wlow, whigh]
#[b, a] = ellip(order, pbrip, sbrip, w, btype='bandpass')

a = (fhigh - flow)/fi*0.1
bands = [0.,flow/fs*(1-a),flow/fs*(1+a),fhigh/fs*(1-a),fhigh/fs*(1+a),0.5]
#bands = [0.,0.001,0.0011,0.0019,0.002,0.5]
print bands
b = remez(numtaps=100000, bands=bands, desired=[0.,1.,0.], weight=None, Hz=1., type='bandpass', maxiter=25, grid_density=64); a = [1.]

yf, zf = lfilter(b, a, y, zi=zeros(max(len(a),len(b))-1))
#yf2, zf = lfilter(b, a, 0.*y, zi=zf)
#yf3, zf = lfilter(b, a, 0.*y, zi=zf)

impulse = zeros(N); impulse[0] = 1.
yf_imp, zf = lfilter(b, a, impulse, zi=zeros(max(len(a),len(b))-1))

clf()
subplot(311); plot(x,y); plot(x, yf)#; plot(x[-1]+x, yf2); plot(2*x[-1]+x, yf3)
subplot(312); semilogx(fftshift(fftfreq(N,1./fs))[N/2:],fftshift(20.*log(abs(fft(y))))[N/2:]); semilogx(fftshift(fftfreq(N,1./fs))[N/2:],fftshift(20.*log(abs(fft(yf))))[N/2:]); ylim(ymin=1e-6)
#subplot(313); w, h = freqz(b, a, worN=N); loglog(w, abs(h)**2)
subplot(313); semilogx(fftshift(fftfreq(N,1./fs))[N/2:],fftshift(20.*log(abs(fft(yf_imp))))[N/2:])
show()