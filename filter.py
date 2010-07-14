# -*- coding: utf-8 -*-
from numpy import arange, sqrt, zeros
# the three following lines are a workaround for a bug with scipy and py2exe
# together. See http://www.pyinstaller.org/ticket/83 for reference.
from scipy.misc import factorial
import scipy
scipy.factorial = factorial

from scipy.signal import lfilter
import pickle

NOCTAVE = 8

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

def octave_filter_bank(forward, feedback, x, zis=None):
	# This function filters the waveform x with the array of filters
	# specified by the forward and feedback parameters. Each row
	# of the forward and feedback parameters are the parameters
	# to the Matlab builtin function "filter".
	Nbank = len(forward)
	y = zeros((Nbank, len(x)))
	
	zfs = []
	y = []
	
	if zis == None:
		zis = []
		for i in range(0, Nbank):
			zis += [zeros(max(len(forward[i]), len(feedback[i]))-1)] 
	
	for i in range(0, Nbank):
		filt, zf = lfilter(forward[i], feedback[i], x, zi=zis[i])
		# zf can be reused to restart the filter
		zfs += [zf]
		y += [filt]
		
	return y, zfs

# Note: we may have one filter in excess here : the low-pass filter for decimation
# does approximately the same thing as the low-pass component of the highest band-pass
# filter for the octave
def octave_filter_bank_decimation(blow, alow, forward, feedback, x, zis=None):
	# This function filters the waveform x with the array of filters
	# specified by the forward and feedback parameters. Each row
	# of the forward and feedback parameters are the parameters
	# to the Matlab builtin function "filter".
	BandsPerOctave = len(forward)
	Nbank = NOCTAVE*BandsPerOctave
	
	y = [0.]*Nbank
	dec = [0.]*Nbank
	
	x_dec = x
	
	zfs = []
	
	if zis == None:
		m = 0
		k = Nbank - 1
	
		for j in range(0, NOCTAVE):
			for i in range(0, BandsPerOctave)[::-1]:
				filt = lfilter(forward[i], feedback[i], x_dec)
				m += 1
				y[k] = filt
				dec[k] = 2**j
				k -= 1
			x_dec = lfilter(blow, alow, x_dec)
			m += 1
			x_dec = x_dec[::2]
		
		return y, dec, None
	else:
		m = 0
		k = Nbank - 1
		
		for j in range(0, NOCTAVE):
			for i in range(0, BandsPerOctave)[::-1]:
				filt, zf = lfilter(forward[i], feedback[i], x_dec, zi=zis[m])
				#filt = lfilter(forward[i], feedback[i], x_dec)
				m += 1
				# zf can be reused to restart the filter
				zfs += [zf]
				#zfs += [0.]
				y[k] = filt
				dec[k] = 2**j
				k -= 1
			x_dec, zf = lfilter(blow, alow, x_dec, zi=zis[m])
			#x_dec = lfilter(blow, alow, x_dec)
			m += 1
			# zf can be reused to restart the filter
			zfs += [zf]
			#zfs += [0.]
			x_dec = x_dec[::2]
		
		return y, dec, zfs

def load_filters_params():
	input = open('generated_filters.pkl', 'rb')
	# Pickle dictionary using protocol 0.
	params = pickle.load(input)
	# Pickle the list using the highest protocol available.
	#pickle.load(input, -1)
	input.close()
	
	return params
