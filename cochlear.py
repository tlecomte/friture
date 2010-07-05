# -*- coding: utf-8 -*-
from numpy import pi, exp, arange, cos, sin, sqrt, zeros, ones, log, arange
# the three following lines are a workaround for a bug with scipy and py2exe
# together. See http://www.pyinstaller.org/ticket/83 for reference.
from scipy.misc import factorial
import scipy
scipy.factorial = factorial
from scipy.signal import lfilter
from scipy.signal.filter_design import ellip, butter

# bank of filters for any other kind of frequency scale
# http://cobweb.ecn.purdue.edu/~malcolm/apple/tr35/PattersonsEar.pdf
# bandwidth of a cochlear channel as a function of center frequency

# Change the following parameters if you wish to use a different
# ERB scale.
EarQ = 9.26449 # Glasberg and Moore Parameters
minBW = 24.7
order = 1.

def frequencies(fs, numChannels, lowFreq):
	channels = arange(0, numChannels)
	cf = -(EarQ*minBW) + exp(channels*(-log(fs/2 + EarQ*minBW) + \
		log(lowFreq + EarQ*minBW))/numChannels) \
		*(fs/2 + EarQ*minBW)
	return cf

def MakeERBFilters(fs, numChannels, lowFreq):
	# [forward, feedback] = MakeERBFilters(fs, numChannels) computes the
	# filter coefficients for a bank of Gammatone filters. These
	# filters were defined by Patterson and Holdworth for simulating
	# the cochlea. The results are returned as arrays of filter
	# coefficients. Each row of the filter arrays (forward and feedback)
	# can be passed to the MatLab "filter" function, or you can do all
	# the filtering at once with the ERBFilterBank() function.
	#
	# The filter bank contains "numChannels" channels that extend from
	# half the sampling rate (fs) to "lowFreq".
	T = 1./fs
	# All of the following expressions are derived in Apple TR #35, "An
	# Efficient Implementation of the Patterson-Holdsworth Cochlear
	# Filter Bank."
	cf = frequencies(fs, numChannels, lowFreq)
	ERB = ((cf/EarQ)**order + minBW**order)**(1./order)
	B = 1.019*2*pi*ERB
	gain = abs((-2*exp(4*1j*cf*pi*T)*T + \
		   2*exp(-(B*T) + 2*1j*cf*pi*T)*T* \
		   (cos(2*cf*pi*T) - sqrt(3. - 2.**(3./2.))* \
		   sin(2*cf*pi*T))) * \
		   (-2*exp(4*1j*cf*pi*T)*T + \
		   2*exp(-(B*T) + 2*1j*cf*pi*T)*T* \
		   (cos(2*cf*pi*T) + sqrt(3. - 2.**(3./2.)) * \
		   sin(2*cf*pi*T)))* \
		   (-2*exp(4*1j*cf*pi*T)*T + \
		   2*exp(-(B*T) + 2*1j*cf*pi*T)*T* \
		   (cos(2*cf*pi*T) - \
		   sqrt(3. + 2.**(3./2.))*sin(2*cf*pi*T))) * \
		   (-2*exp(4*1j*cf*pi*T)*T + 2*exp(-(B*T) + 2*1j*cf*pi*T)*T* \
		   (cos(2*cf*pi*T) + sqrt(3. + 2.**(3./2.))*sin(2*cf*pi*T))) / \
		   (-2 / exp(2*B*T) - 2*exp(4*1j*cf*pi*T) + \
		   2*(1 + exp(4*1j*cf*pi*T))/exp(B*T))**4)
	
	feedback = zeros((len(cf), 9))
	forward = zeros((len(cf), 5))
	forward[:,0] = T**4 / gain
	forward[:,1] = -4*T**4*cos(2*cf*pi*T)/exp(B*T)/gain
	forward[:,2] = 6*T**4*cos(4*cf*pi*T)/exp(2*B*T)/gain
	forward[:,3] = -4*T**4*cos(6*cf*pi*T)/exp(3*B*T)/gain
	forward[:,4] = T**4*cos(8*cf*pi*T)/exp(4*B*T)/gain
	feedback[:,0] = ones(len(cf))
	feedback[:,1] = -8*cos(2*cf*pi*T)/exp(B*T)
	feedback[:,2] = 4*(4 + 3*cos(4*cf*pi*T))/exp(2*B*T)
	feedback[:,3] = -8*(6*cos(2*cf*pi*T) + cos(6*cf*pi*T))/exp(3*B*T)
	feedback[:,4] = 2*(18 + 16*cos(4*cf*pi*T) + cos(8*cf*pi*T))/exp(4*B*T)
	feedback[:,5] = -8*(6*cos(2*cf*pi*T) + cos(6*cf*pi*T))/exp(5*B*T)
	feedback[:,6] = 4*(4 + 3*cos(4*cf*pi*T))/exp(6*B*T)
	feedback[:,7] = -8*cos(2*cf*pi*T)/exp(7*B*T)
	feedback[:,8] = exp(-8*B*T)

	return [forward, feedback]

def ERBFilterBank(forward, feedback, x):
	# y=ERBFilterBank(forward, feedback, x)
	# This function filters the waveform x with the array of filters
	# specified by the forward and feedback parameters. Each row
	# of the forward and feedback parameters are the parameters
	# to the Matlab builtin function "filter".
	(rows, cols) = feedback.shape
	y = zeros((rows, len(x)))
	for i in range(0, rows):
		y[i,:] = lfilter(forward[i,:], feedback[i,:], x)
	return y

# Nominal frequencies: 31.5 40 50 63 80 100 125 160 200 250 315 400 500 630 800 1000 1250
# 1600 2000 Hz, etc.
def octave_frequencies(Nbands, BandsPerOctave):
	f0 = 1000. # audio reference frequency is 1 kHz
	
	b = 1./BandsPerOctave
	
	imax = Nbands/2
	if Nbands%2 == 1:
		i = arange(-imax, imax + 1)
	else:
		i = arange(-imax, imax) + 0.5
	
	fi = f0 * 2**(i*b)
	f_low = fi * sqrt(2**(-b))
	f_high = fi * sqrt(2**b)
	
	return fi, f_low, f_high

def octave_filters(Nbands, BandsPerOctave):
	# Bandpass Filter Generation
	pbrip = .5	# Pass band ripple
	sbrip = 30	# Stop band rejection

	fi, f_low, f_high = octave_frequencies(Nbands, BandsPerOctave)

	fs = 44100 # sampling rate
	wi = fi/(fs/2.) # normalized frequencies
	w_low = f_low/(fs/2.)
	w_high = f_high/(fs/2.)

	B = []
	A = []
	
	# For each band
	for w, wl, wh in zip(wi, w_low, w_high):
		# normalized frequency vector
		freq = [wl, wh]
			
		#Filter order
		order = 2
	
		# could be another IIR filter
		[b, a] = ellip(order, pbrip, sbrip, freq, btype='bandpass')
		
		B += [b]
		A += [a]
		
	return [B, A, fi, f_low, f_high]

# Note : A way to make the filtering more efficient is to do it with IIR + decimation
# instead of IIR only
# More precisely, we design as much filters as bands per octave (instead of total number
# of bands), and apply it several times on repeatedly decimated signal to go from one octave
# to its lower neighbor
def octave_filters_oneoctave(Nbands, BandsPerOctave):
	# Bandpass Filter Generation
	pbrip = .5	# Pass band ripple
	sbrip = 80	# Stop band rejection

	fi, f_low, f_high = octave_frequencies(Nbands, BandsPerOctave)

	fi     = fi[-BandsPerOctave:]
	f_low  = f_low[-BandsPerOctave:]
	f_high = f_high[-BandsPerOctave:]

	fs = 44100 # sampling rate
	wi = fi/(fs/2.) # normalized frequencies
	w_low = f_low/(fs/2.)
	w_high = f_high/(fs/2.)

	B = []
	A = []
	
	# For each band
	for w, wl, wh in zip(wi, w_low, w_high):
		# normalized frequency vector
		freq = [wl, wh]
			
		#Filter order
		order = 2
	
		# could be another IIR filter
		[b, a] = ellip(order, pbrip, sbrip, freq, btype='bandpass')
		
		B += [b]
		A += [a]
		
	return [B, A, fi, f_low, f_high]

def octave_filter_bank(forward, feedback, x):
	# This function filters the waveform x with the array of filters
	# specified by the forward and feedback parameters. Each row
	# of the forward and feedback parameters are the parameters
	# to the Matlab builtin function "filter".
	Nbank = len(forward)
	y = zeros((Nbank, len(x)))
	for i in range(0, Nbank):
		y[i,:] = lfilter(forward[i], feedback[i], x)
	return y

# Note: we may have one filter in excess here : the low-pass filter for decimation
# does approximately the same thing as the low-pass component of the highest band-pass
# filter for the octave
def octave_filter_bank_decimation(blow, alow, forward, feedback, x, zis=None):
	# This function filters the waveform x with the array of filters
	# specified by the forward and feedback parameters. Each row
	# of the forward and feedback parameters are the parameters
	# to the Matlab builtin function "filter".
	BandsPerOctave = len(forward)
	Nbank = 8*BandsPerOctave
	
	y = []
	dec = []
	
	x_dec = x
	
	zfs = []
	
	m = 0
	
	for j in range(0, 8):
		for i in range(0, BandsPerOctave)[::-1]:
			if zis == None:
				zi = zeros(max(len(forward[i]), len(feedback[i]))-1) 
			else:
				zi = zis[m]
				m += 1
			filt, zf = lfilter(forward[i], feedback[i], x_dec, zi=zi)
			# zf can be reused to restart the filter
			zfs += [zf]
			y += [filt]
			dec += [2**j]
		if zis == None:
			zi = zeros(max(len(blow),len(alow))-1)
		else:
			zi = zis[m]
			m += 1
		x_dec, zf = lfilter(blow, alow, x_dec, zi=zi)
		# zf can be reused to restart the filter
		zfs += [zf]
		x_dec = x_dec[::2]
	
	return y, dec, zfs

# main() is a test function
def main():
	from matplotlib.pyplot import semilogx, plot, show, xlim, ylim
	from numpy.fft import fft, fftfreq
	from numpy import log10, linspace

	N = 2048*2*2
	fs = 44100.
	Nchannels = 20
	low_freq = 20.

	impulse = zeros(N)
	impulse[0] = 1
	#impulse = sin(linspace(0, 600*pi, N))

	[ERBforward, ERBfeedback] = MakeERBFilters(fs, Nchannels, low_freq)
	y = ERBFilterBank(ERBforward, ERBfeedback, impulse)

	Nbands = 7
	BandsPerOctave = 1
	[B, A, fi, fl, fh] = octave_filters(Nbands, BandsPerOctave)
	y = octave_filter_bank(B, A, impulse)

	response = 20.*log10(abs(fft(y)))
	freqScale = fftfreq(N, 1./fs)

	for i in range(0, response.shape[0]):
			semilogx(freqScale[0:N/2],response[i, 0:N/2])
	xlim(fs/2000, fs)
	ylim(-70, 10)

	show()
	
if __name__ == "__main__":
	main()
