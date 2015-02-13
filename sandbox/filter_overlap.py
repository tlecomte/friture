from pylab import *
from scipy.signal.filter_design import ellip
from scipy.signal.signaltools import lfilter

figure()
N = 2**13
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
[b, a] = ellip(order, pbrip, sbrip, w, btype='bandpass')

yf, zf = lfilter(b, a, y, zi=zeros(max(len(a),len(b))-1))
yf2, zf = lfilter(b, a, 0.*y, zi=zf)
yf3, zf = lfilter(b, a, 0.*y, zi=zf)

print(x[-1]+x, yf2)

clf()
subplot(211); plot(x,y); plot(x, yf); plot(x[-1]+x, yf2); plot(2*x[-1]+x, yf3)
subplot(212); loglog(fftshift(fftfreq(N,1./fs))[N/2:],fftshift(abs((fft(y)))**2)[N/2:]); loglog(fftshift(fftfreq(N,1./fs))[N/2:],fftshift(abs((fft(yf)))**2)[N/2:]); ylim(ymin=1e-6)
show()