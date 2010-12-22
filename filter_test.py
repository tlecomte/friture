# -*- coding: utf-8 -*-
from numpy import pi, exp, arange, cos, sin, sqrt, zeros, ones, log, arange
# the three following lines are a workaround for a bug with scipy and py2exe
# together. See http://www.pyinstaller.org/ticket/83 for reference.
from scipy.misc import factorial
import scipy
scipy.factorial = factorial

#importing from scipy.signal.signaltools and scipy.signal.filter_design instead of scipy.signal
#decreases dramatically the number of modules imported
from scipy.signal.signaltools import lfilter
from scipy.signal.filter_design import ellip, butter, firwin, cheby1, iirdesign, freqz

from filter import octave_frequencies

NOCTAVE = 8

def octave_filters(Nbands, BandsPerOctave):
	# Bandpass Filter Generation
	pbrip = .5	# Pass band ripple
	sbrip = 50	# Stop band rejection
	#Filter order
	order = 2

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
	sbrip = 50	# Stop band rejection
	#Filter order
	order = 2

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
	
		# could be another IIR filter
		[b, a] = ellip(order, pbrip, sbrip, freq, btype='bandpass')
		
		B += [b]
		A += [a]
		
	return [B, A, fi, f_low, f_high]

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
		#filt, zf = lfilter(forward[i], feedback[i], x, zi=zis[i])
		filt, zf = double_filt(forward[i], feedback[i], x, zis[i])
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
				#filt = lfilter(forward[i], feedback[i], x_dec)
				filt, z_unused = double_filt(forward[i], feedback[i], x_dec, zeros(max(len(forward[i]),len(feedback[i]))))
				m += 1
				y[k] = filt
				dec[k] = 2**j
				k -= 1
			#x_dec = lfilter(blow, alow, x_dec)
			x_dec, z_unused = double_filt(blow, alow, x_dec, zeros(max(len(blow),len(alow))))
			m += 1
			x_dec = x_dec[::2]
		
		return y, dec, None
	else:
		m = 0
		k = Nbank - 1
		
		for j in range(0, NOCTAVE):
			for i in range(0, BandsPerOctave)[::-1]:
				#filt, zf = lfilter(forward[i], feedback[i], x_dec, zi=zis[m])
				filt, zf = double_filt(forward[i], feedback[i], x, zis[m])
				#filt = lfilter(forward[i], feedback[i], x_dec)
				m += 1
				# zf can be reused to restart the filter
				zfs += [zf]
				#zfs += [0.]
				y[k] = filt
				dec[k] = 2**j
				k -= 1
			#x_dec, zf = lfilter(blow, alow, x_dec, zi=zis[m])
			x_dec, zf = double_filt(blow, alow, x_dec, zis[m])
			#x_dec = lfilter(blow, alow, x_dec)
			m += 1
			# zf can be reused to restart the filter
			zfs += [zf]
			#zfs += [0.]
			x_dec = x_dec[::2]
		
		return y, dec, zfs

def double_filt(b, a, x, Z):
	#The filter function is implemented as a direct II transposed structure.
	#This means that the filter implements:

	#a[0]*y[n] = b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb]
			#- a[1]*y[n-1] - ... - a[na]*y[n-na]

	#using the following difference equations::

	#y[m] = b[0]*x[m] + z[0,m-1]
	#z[0,m] = b[1]*x[m] + z[1,m-1] - a[1]*y[m]
	#...
	#z[n-3,m] = b[n-2]*x[m] + z[n-2,m-1] - a[n-2]*y[m]
	#z[n-2,m] = b[n-1]*x[m] - a[n-1]*y[m]
         
	# b and a must have the same length
	if len(a) > len(b):
		b = append((b, zeros(len(a) - len(b))))
	elif len(a) < len(b):
		a = append((a, zeros(len(b) - len(a))))
         
	# Normalize by a[0]
	b = b/a[0]
	a[1:] = a[1:]/a[0]
	
	#define y
	y = zeros(x.shape)
         
	for k in range(0, len(x)):
		i = 0 # Reset a and b pointers
		xn = x[k]
		if len(b) > 1:
			j = 0
			# Calculate first delay (output)
			y[k] = Z[j] + b[i]*xn
			i = i + 1
			# Fill in middle delays
			for n in range(0, len(b) - 2):
				Z[j] = Z[j+1] + xn*b[i] - y[k]*a[i]
				i = i + 1
				j = j + 1
			# Calculate last delay
			Z[j] = xn*b[i] - y[k]*a[i]
		else:
			y[k] = xn*b[i]

	return y, Z

# main() is a test function
def main():
	from matplotlib.pyplot import semilogx, plot, show, xlim, ylim, figure, legend, subplot, bar
	from numpy.fft import fft, fftfreq, fftshift, ifft
	from numpy import log10, linspace, interp, angle, array, concatenate

	N = 2048*2*2
	fs = 44100.
	Nchannels = 20
	low_freq = 20.

	impulse = zeros(N)
	impulse[N/2] = 1
	f = 1000.
	#impulse = sin(2*pi*f*arange(0, N/fs, 1./fs))

	#[ERBforward, ERBfeedback] = MakeERBFilters(fs, Nchannels, low_freq)
	#y = ERBFilterBank(ERBforward, ERBfeedback, impulse)

	BandsPerOctave = 1
	Nbands = NOCTAVE*BandsPerOctave
	
	[B, A, fi, fl, fh] = octave_filters(Nbands, BandsPerOctave)
	y, zfs = octave_filter_bank(B, A, impulse)
	
	response = 20.*log10(abs(fft(y)))
	freqScale = fftfreq(N, 1./fs)
	
	figure()
	subplot(211)
	
	for i in range(0, response.shape[0]):
		semilogx(freqScale[0:N/2],response[i, 0:N/2])
		
	xlim(fs/2000, fs)
	ylim(-70, 10)
	
	subplot(212)
	m = 0
	for f in fi:
		p = 10.*log10((y[m]**2).mean())
		m += 1
		semilogx(f, p, 'ko')
	
	Ndec = 3
	fc = 0.5
	# other possibilities
	#(bdec, adec) = ellip(Ndec, 0.05, 30, fc)
	#print bdec
	#(bdec, adec) = cheby1(Ndec, 0.05, fc)
	#(bdec, adec) = butter(Ndec, fc)
	(bdec, adec) = iirdesign(0.48, 0.50, 0.05, 70, analog=0, ftype='ellip', output='ba')
	#bdec = firwin(30, fc)
	#adec = [1.]
	
	figure()
	subplot(211)
	
	response = 20.*log10(abs(fft(impulse)))
	plot(fftshift(freqScale), fftshift(response), label="impulse")
	
	y = lfilter(bdec, adec, impulse)
	response = 20.*log10(abs(fft(y)))
	plot(fftshift(freqScale), fftshift(response), label="lowpass")
	
	ydec = y[::2].repeat(2)
	response = 20.*log10(abs(fft(ydec)))
	plot(fftshift(freqScale), fftshift(response), label="lowpass + dec2 + repeat2")
	
	ydec2 = interp(range(0, len(y)), range(0, len(y), 2), y[::2])
	response = 20.*log10(abs(fft(ydec2)))
	plot(fftshift(freqScale), fftshift(response), label="lowpass + dec2 + interp2")
	
	ydec3 = y[::2]
	response = 20.*log10(abs(fft(ydec3)))
	freqScale2 = fftfreq(N/2, 2./fs)
	plot(freqScale2,fftshift(response), label="lowpass + dec2")
	
	legend(loc="lower left")
	
	subplot(212)
	plot(range(0, len(impulse)), impulse, label="impulse")
	plot(range(0, len(impulse)), y, label="lowpass")
	plot(range(0, len(impulse)), ydec, label="lowpass + dec2 + repeat2")
	plot(range(0, len(impulse)), ydec2, label="lowpass + dec2 + interp2")
	plot(range(0, len(impulse), 2), ydec3, label="lowpass + dec2")
	legend()
	
	[boct, aoct, fi, flow, fhigh] = octave_filters_oneoctave(Nbands, BandsPerOctave)
	y, dec, zfs = octave_filter_bank_decimation(bdec, adec, boct, aoct, impulse)

	figure()
	subplot(211)
	
	for yone, d in zip(y, dec):
		response = 20.*log10(abs(fft(yone))*d)
		freqScale = fftfreq(N/d, 1./(fs/d))
		semilogx(freqScale[0:N/(2*d)],response[0:N/(2*d)])
	
	xlim(fs/2000, fs)
	ylim(-70, 10)
	
	subplot(212)
	m = 0
	for i in range(0, NOCTAVE):
		for f in fi:
			p = 10.*log10((y[m]**2).mean())
			semilogx(f/dec[m], p, 'ko')
			m += 1

	[boct, aoct, fi, flow, fhigh] = octave_filters_oneoctave(Nbands, BandsPerOctave)
	y1, dec, zfs = octave_filter_bank_decimation(bdec, adec, boct, aoct, impulse[0:N/2])
	y2, dec, zfs = octave_filter_bank_decimation(bdec, adec, boct, aoct, impulse[N/2:], zis=zfs)	
	
	y = []
	for y1one, y2one in zip(y1,y2):
		y += [concatenate((y1one,y2one))]

	figure()
	subplot(211)
	
	for yone, d in zip(y, dec):
		response = 20.*log10(abs(fft(yone))*d)
		freqScale = fftfreq(N/d, 1./(fs/d))
		semilogx(freqScale[0:N/(2*d)],response[0:N/(2*d)])
	
	xlim(fs/2000, fs)
	ylim(-70, 10)
	
	subplot(212)
	m = 0
	for i in range(0, NOCTAVE):
		for f in fi:
			p = 10.*log10((y[m]**2).mean())
			semilogx(f/dec[m], p, 'ko')
			m += 1

	show()
	
if __name__ == "__main__":
	main()
