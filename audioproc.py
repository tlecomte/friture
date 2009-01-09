import numpy

def analyzelive(data, point, fft_size):
	samples = data.floatdata[point:point + fft_size]
#	samples *= window
	fft = numpy.fft.fft(samples)
	spectrum = numpy.abs(fft[:fft.shape[0] / 2 + 1]) / float(fft_size)
	return spectrum
