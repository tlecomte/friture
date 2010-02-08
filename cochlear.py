from numpy import pi, exp, arange, cos, sin, sqrt

def MakeERBFilters(fs,numChannels,lowFreq):
	# [forward, feedback]=MakeERBFilters(fs,numChannels) computes the
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
	channels = arange(1, numChannels)
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
	       2*exp(-(B*T) + 2*1j*cf*pi*T)*T.* \
	       (cos(2*cf*pi*T) + sqrt(3. - 2.**(3./2.)) * \
	       sin(2*cf*pi*T)))* \
	       (-2*exp(4*1j*cf*pi*T)*T + \
	       2*exp(-(B*T) + 2*1j*cf*pi*T)*T* \
	       (cos(2*cf*pi*T) - \
	       sqrt(3. + 2.**(3./2.))*sin(2*cf*pi*T))) * \
	       (-2*exp(4*1j*cf*pi*T)*T + 2*exp(-(B*T) + 2*1j*cf*pi*T)*T* \
	       (cos(2*cf*pi*T) + sqrt(3. + 2.**(3./2).)*sin(2*cf*pi*T))) / \
	       (-2 / exp(2*B*T) - 2*exp(4*1j*cf*pi*T) + \
	       2*(1 + exp(4*1j*cf*pi*T))/exp(B*T))**4)
	
	feedback = zeros(length(cf), 9)
	forward = zeros(length(cf), 5)
	forward(:,1) = T**4 ./ gain
	forward(:,2) = -4*T**4*cos(2*cf*pi*T)./exp(B*T)./gain
	forward(:,3) = 6*T**4*cos(4*cf*pi*T)./exp(2*B*T)./gain
	forward(:,4) = -4*T**4*cos(6*cf*pi*T)./exp(3*B*T)./gain
	forward(:,5) = T**4*cos(8*cf*pi*T)./exp(4*B*T)./gain
	feedback(:,1) = ones(length(cf),1)
	feedback(:,2) = -8*cos(2*cf*pi*T)./exp(B*T)
	feedback(:,3) = 4*(4 + 3*cos(4*cf*pi*T))./exp(2*B*T)
	feedback(:,4) = -8*(6*cos(2*cf*pi*T) + cos(6*cf*pi*T))./exp(3*B*T)
	feedback(:,5) = 2*(18 + 16*cos(4*cf*pi*T) + cos(8*cf*pi*T))./exp(4*B*T)
	feedback(:,6) = -8*(6*cos(2*cf*pi*T) + cos(6*cf*pi*T))./exp(5*B*T)
	feedback(:,7) = 4*(4 + 3*cos(4*cf*pi*T))./exp(6*B*T)
	feedback(:,8) = -8*cos(2*cf*pi*T)./exp(7*B*T)
	feedback(:,9) = exp(-8*B*T)

	return [forward, feedback]

def ERBFilterBank(forward, feedback, x):
	# y=ERBFilterBank(forward, feedback, x)
	# This function filters the waveform x with the array of filters
	# specified by the forward and feedback parameters. Each row
	# of the forward and feedback parameters are the parameters
	# to the Matlab builtin function "filter".
	[rows, cols] = size(feedback)
	y = zeros(rows,length(x))
	for i in range(1,rows):
		y(i,:) = filter(forward(i,:),feedback(i,:),x)
	return y

impulse = [1 zeros(1,1023)]
[ERBforward, ERBfeedback] = MakeERBFilters(16000, 64, 20)
y = ERBFilterBank(ERBforward, ERBfeedback, impulse)

response = 20*log10(abs(fft(y[1:64:5,:])))
channels_ind = arange(0, 1023)
freqScale = channels_ind/1024*16000
axis([2 4 -70 10])
semilogx(freqScale(1:512),response(1:512,:))