# -*- coding: utf-8 -*-
from numpy import pi, exp, arange, cos, sin, sqrt, zeros, ones, log, arange
# the three following lines are a workaround for a bug with scipy and py2exe
# together. See http://www.pyinstaller.org/ticket/83 for reference.
from scipy.misc import factorial
import scipy
scipy.factorial = factorial
from scipy.signal import lfilter
from scipy.signal.filter_design import ellip

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

#1/3 octave (or 1/10 decade) in audio means (ISO R 266 and ANSI S1.6-1984):
#fc[n]=10*e^(n/10) 15<=n<=43
#or
#fc[k]=2^k/3*1000Hz

#Nominal freq: 31.5 40 50 63 80 100 125 160 200 250 315 400 500 630 800 1000 1250
#1600 2000 Hz, etc.
#The upper and lower band edges are:
#fcl=sqrt(fc[k-1]*fc[k])
#fch=sqrt(fc[k]*fc[k+1])
#def octave_frequencies():

def octave_filters(Nchannels):
	# Bandpass Filter Generation

	fstart = 0.05      # Start frequency
	fend = 0.95        # End frequency
	pbrip = .5         # Pass band ripple
	sbrip = 30         # Stop band rejection

	K = arange(fstart, fend, (fend-fstart)/Nchannels)
	B = []
	A = []
	
	# For each frequency bin
	for k in K:
		# Scale fails by default
		fail = 1
		scale = 1

		while fail == 1:
			#The scale has to be adjusted so that filter coefficients are
			# -1.0<coeff<1.0
			#Scaling performed is 2^(-scale)
			
			#For lowpass, set equal to normalized Freq (cutoff/(Fs/2))
			#For bandpass, set equal to normalized Freq vector ([low high]/(Fs/2))
			freq = [k, k+(fend-fstart)/(2*Nchannels)]
			
			#Filter order:
			#	use 2,4 for lowpass
			#		1,2 for bandpass
			#NOTE that for a bandpass filter (order) poles are generated for the high
			#and low cutoffs, so the total order is (order)*2
			order = 2
	
			#could also use butter, or cheby1 or cheby2 or besself
			# but note that besself is lowpass only!
			[b, a] = ellip(order, pbrip, sbrip, freq, btype='bandpass')
	
			b = b * (2**-scale)
			a = -a * (2**-scale)
	
			# Keep increasing scale until coeffs are safe
			if sum(abs(b) >= 1) | sum(abs(a) >= 1):
				fail = 1
				scale = scale + 1
				print 'Retrying %f with new scale factor %d' %(k, scale)
			else:
				fail = 0
	
		ordera = order*len(freq)
		if ordera==2:
			scstr = 'IIR2 filter'
		elif ordera==4:
			scstr = 'IIR4 filter'
		else:
			error('order*length(freq) must equal 2 or 4')
	
		[b, a] = ellip(order, pbrip, sbrip, freq, btype='bandpass')
		
		B += [b]
		A += [a]
		
	return [B, A]

	##sampling rate on DE2 board
	#Fs = 8000
	#[fresponse, ffreq] = freqz(b,a,1000)
	#plot(ffreq/pi*Fs/2,abs(fresponse))
	#b = fix((b*(2**-scale))*2**16)/2**16
	#a = fix((a*(2**-scale))*2**16)/2**16
	#[fresponse, ffreq] = freqz(b,a,1000)
	#plot(ffreq/pi*Fs/2,abs(fresponse))
	#legend('exact','scaled 16-bit')

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

# main() is a test function
def main():
    from matplotlib.pyplot import semilogx, plot, show, xlim, ylim
    from numpy.fft import fft, fftfreq
    from numpy import log10, linspace

    N = 2048
    fs = 44100.
    Nchannels = 20
    low_freq = 20.

    impulse = zeros(N)
    impulse[0] = 1
    #impulse = sin(linspace(0, 600*pi, N))

    [ERBforward, ERBfeedback] = MakeERBFilters(fs, Nchannels, low_freq)
    y = ERBFilterBank(ERBforward, ERBfeedback, impulse)
    
    [B, A] = octave_filters(Nchannels)
    y = octave_filter_bank(B, A, impulse)

    response = 20.*log10(abs(fft(y)))
    freqScale = fftfreq(N, 1./fs)

    for i in range(0, response.shape[0]):
            semilogx(freqScale[0:N/2],response[i, 0:N/2])
    xlim(fs/100, fs)
    ylim(-70, 10)

    show()
    
if __name__ == "__main__":
    main()
