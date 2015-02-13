from pylab import *
from scipy.signal.filter_design import ellip, freqz, iirdesign
from scipy.signal.fir_filter_design import remez
from scipy.signal.signaltools import lfilter

figure()

N = 2**13
fs = 44100.
x = arange(0,N)/fs
f1 = 18000.
f2 = 2000.
#signal
y = sin(2*pi*x*f1) + sin(2*pi*x*f2)

#window
Nw = 2**13
window = zeros(N)
window[:Nw] = hamming(Nw)

# windowed signal
y *= window

Ntaps = 512
b_fir = remez(numtaps=Ntaps, bands=[0., 0.49/2., 0.51/2., 1./2.], desired=[1.,0.])#, maxiter=250, grid_density=64)
a_fir = [1.]
print("FIR coeff created", len(b_fir), len(a_fir))

def fft_overlap_add_lfilter(b, x, zi):  
    # Evaluate the best value of N and L
    M = len(b) # length o f the filters
    L = 5*M # length of the segments
    N = L + M - 1 # length of the convolutions, should be power of two, must be larger than L + M - 1
    Nx = len(x) # total length of the signal
    
    y = np.zeros((len(x)))
    
    bf = rfft(b, n=N) # zero-padded FFT

    i = 0
    while i<Nx:
        il = min(i+L, Nx)
        yt = irfft(rfft(x[i:il], n=N)*bf, n=N) # compute the convolution on the segment
        k = min(i+N, Nx)
        y[i:k] += yt[:k-i] # add the overlapped output blocks
        i += L
    
    #check if we have enough samples available
    #and compute number of fft to be done
    
    zf = 0.
    
    return y, zf


import time
t0 = time.time()
yf_fir, zf = lfilter(b_fir, a_fir, y, zi=zeros(max(len(a_fir),len(b_fir))-1))
t1 = time.time()
yf_fir_oa, zf = fft_overlap_add_lfilter(b_fir, y, zi=zeros(max(len(a_fir),len(b_fir))-1))
t2 = time.time()
tlin = t1 - t0
toa = t2 - t1
print("lin", tlin, "o-a", toa, "lin/o-a", tlin/toa)

impulse = zeros(N); impulse[0] = 1.
yf_imp_fir, zf = lfilter(b_fir, a_fir, impulse, zi=zeros(max(len(a_fir),len(b_fir))-1))
yf_imp_fir_oa, zf = fft_overlap_add_lfilter(b_fir, impulse, zi=zeros(max(len(a_fir),len(b_fir))-1))
#yf_imp_iir, zf = lfilter(b_iir, a_iir, impulse, zi=zeros(max(len(a_iir),len(b_iir))-1))

clf()

subplot(311)
title("original and filtered signals")
plot(x, y)
plot(x, yf_fir)
plot(x, yf_fir_oa)

subplot(312)
title("original and filtered frequency distributions")
semilogx(fftshift(fftfreq(N,1./fs))[N/2:], fftshift(20.*log(abs(fft(y))))[N/2:])
semilogx(fftshift(fftfreq(N,1./fs))[N/2:], fftshift(20.*log(abs(fft(yf_fir))))[N/2:])
semilogx(fftshift(fftfreq(N,1./fs))[N/2:], fftshift(20.*log(abs(fft(yf_fir_oa))))[N/2:])
ylim(ymin=1e-6)

subplot(313)
title("filter impulse response")
semilogx(fftshift(fftfreq(N,1./fs))[N/2:], fftshift(20.*log(abs(fft(yf_imp_fir))))[N/2:])
semilogx(fftshift(fftfreq(N,1./fs))[N/2:], fftshift(20.*log(abs(fft(yf_imp_fir_oa))))[N/2:])
#semilogx(fftshift(fftfreq(N,1./fs))[N/2:], fftshift(20.*log(abs(fft(yf_imp_iir))))[N/2:])
show()