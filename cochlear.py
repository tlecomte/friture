from numpy import pi, exp, arange, cos, sin, sqrt, zeros, ones, log
from scipy.signal import lfilter

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
	# Change the following parameters if you wish to use a different
	# ERB scale.
	EarQ = 9.26449 # Glasberg and Moore Parameters
	minBW = 24.7
	order = 1.
	# All of the following expressions are derived in Apple TR #35, "An
	# Efficient Implementation of the Patterson-Holdsworth Cochlear
	# Filter Bank."
	channels = arange(0, numChannels)
	cf = -(EarQ*minBW) + exp(channels*(-log(fs/2 + EarQ*minBW) + \
	     log(lowFreq + EarQ*minBW))/numChannels) \
	     *(fs/2 + EarQ*minBW)
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

# main() is a test function
def main():
    from matplotlib.pyplot import semilogx, plot, show, xlim, ylim
    from numpy.fft import fft, fftfreq
    from numpy import log10, linspace

    N = 2048
    fs = 16000.
    Nchannels = 20
    low_freq = 20.

    impulse = zeros(N)
    impulse[0] = 1
    #impulse = sin(linspace(0, 600*pi, N))

    [ERBforward, ERBfeedback] = MakeERBFilters(fs, Nchannels, low_freq)
    y = ERBFilterBank(ERBforward, ERBfeedback, impulse)

    response = 20.*log10(abs(fft(y)))
    freqScale = fftfreq(N, 1./fs)

    for i in range(0, response.shape[0]):
            semilogx(freqScale[0:N/2],response[i, 0:N/2])
    xlim(1e2, 1e4)
    ylim(-70, 10)

    show()
    
if __name__ == "__main__":
    main()
