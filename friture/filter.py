# -*- coding: utf-8 -*-
from numpy import arange, sqrt, zeros
# the three following lines are a workaround for a bug with scipy and py2exe
# together. See http://www.pyinstaller.org/ticket/83 for reference.
#from scipy.misc import factorial
#import scipy
#scipy.factorial = factorial

#importing lfilter from scipy.signal.signaltools instead of scipy.signal decreases
#dramatically the number of modules imported (and decreases the size of the NSIS package...) 
#from scipy.signal.signaltools import lfilter
#importint _linear_filter itself from sigtools is even better
from scipy.signal.sigtools import _linear_filter

#NOTE: by default scipy.signal.__init__.py imports all of its submodules
#To decrease the py2exe distributions dramatically, these import lines can
#be commented out !

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
		k = Nbank - 1
	
		for j in range(0, NOCTAVE):
			for i in range(0, BandsPerOctave)[::-1]:
				filt = lfilter(forward[i], feedback[i], x_dec)
				y[k] = filt
				dec[k] = 2**j
				k -= 1
   			x_dec, zf = decimate(blow, alow, x_dec)
		
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
			x_dec, zf = decimate(blow, alow, x_dec, zi=zis[m])
			m += 1
			# zf can be reused to restart the filter
			zfs += [zf]
			#zfs += [0.]

		return y, dec, zfs

def decimate(bdec, adec, x, zi=None):
    	if zi == None:
		# utiliser un décimateur polyphase ici !!!
		x_dec = lfilter(bdec, adec, x)
		zf = None
	else:
		# utiliser un décimateur polyphase ici !!!
		x_dec, zf = lfilter(bdec, adec, x, zi=zi)

	x_dec = x_dec[::2]
	return x_dec, zf

# build a proper array of zero initial conditions to start the filters
def octave_filter_bank_decimation_filtic(blow, alow, forward, feedback):
	BandsPerOctave = len(forward)		
	zfs = []
		
	for j in range(0, NOCTAVE):
		for i in range(0, BandsPerOctave)[::-1]:
			l = max(len(forward[i]), len(feedback[i])) - 1
			zfs += [zeros(l)]
		l = max(len(blow), len(alow)) - 1
		zfs += [zeros(l)]
	
	return zfs

def lfilter(b, a, x, axis=-1, zi=None):
    """
    Filter data along one-dimension with an IIR or FIR filter.

    Filter a data sequence, x, using a digital filter.  This works for many
    fundamental data types (including Object type).  The filter is a direct
    form II transposed implementation of the standard difference equation
    (see Notes).

    Parameters
    ----------
    b : array_like
        The numerator coefficient vector in a 1-D sequence.
    a : array_like
        The denominator coefficient vector in a 1-D sequence.  If a[0]
        is not 1, then both a and b are normalized by a[0].
    x : array_like
        An N-dimensional input array.
    axis : int
        The axis of the input data array along which to apply the
        linear filter. The filter is applied to each subarray along
        this axis (*Default* = -1)
    zi : array_like (optional)
        Initial conditions for the filter delays.  It is a vector
        (or array of vectors for an N-dimensional input) of length
        max(len(a),len(b))-1.  If zi=None or is not given then initial
        rest is assumed.  SEE signal.lfiltic for more information.

    Returns
    -------
    y : array
        The output of the digital filter.
    zf : array (optional)
        If zi is None, this is not returned, otherwise, zf holds the
        final filter delay values.

    Notes
    -----
    The filter function is implemented as a direct II transposed structure.
    This means that the filter implements

    ::

       a[0]*y[n] = b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb]
                               - a[1]*y[n-1] - ... - a[na]*y[n-na]

    using the following difference equations::

         y[m] = b[0]*x[m] + z[0,m-1]
         z[0,m] = b[1]*x[m] + z[1,m-1] - a[1]*y[m]
         ...
         z[n-3,m] = b[n-2]*x[m] + z[n-2,m-1] - a[n-2]*y[m]
         z[n-2,m] = b[n-1]*x[m] - a[n-1]*y[m]

    where m is the output sample number and n=max(len(a),len(b)) is the
    model order.

    The rational transfer function describing this filter in the
    z-transform domain is::

                             -1               -nb
                 b[0] + b[1]z  + ... + b[nb] z
         Y(z) = ---------------------------------- X(z)
                             -1               -na
                 a[0] + a[1]z  + ... + a[na] z

    """
    #if isscalar(a):
        #a = [a]
    if zi is None:
        return _linear_filter(b, a, x, axis)
    else:
        return _linear_filter(b, a, x, axis, zi)
