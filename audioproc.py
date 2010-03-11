#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

from numpy import linspace, abs, log2, floor
from numpy.fft import rfft
# the sample rate below should be dynamic, taken from PyAudio/PortAudio
SAMPLING_RATE = 44100

#from cochlear import MakeERBFilters, ERBFilterBank, frequencies

class audioproc():
	def __init__(self):
		self.freq = linspace(0, SAMPLING_RATE/2, 10)
		self.maxfreq = 0
		self.decimation = 0

	def analyzelive(self, samples, fft_size, maxfreq):
		#samples *= window
		# first we remove as much points as possible
		if maxfreq <> self.maxfreq:
			self.maxfreq = maxfreq
			decimation = SAMPLING_RATE / (2*maxfreq)
			self.decimation = 2**(floor(log2(decimation)))
		
		if self.decimation < 1:
			self.decimation = 1
		
		samples.shape = len(samples)/self.decimation, self.decimation			
		#the full way
		#samples = samples.mean(axis=1)
		#the simplest way
		samples = samples[:,0]
		
		#uncomment the following to disable the decimation altogether
		#decimation = 1
		
		# FFT for a linear transformation in frequency scale
		fft = rfft(samples)
		spectrum = abs(fft) / float(fft_size/self.decimation)

		if len(self.freq) <> fft_size/2/self.decimation + 1 :
			print "audioproc: updating self.freq cache"
			self.freq = linspace(0, SAMPLING_RATE/2/self.decimation, fft_size/2/self.decimation + 1)
		return spectrum, self.freq

	# above is done a FFT of the signal. This is ok for linear frequency scale, but
	# not satisfying for logarithmic scale, which is much more adapted to voice or music
	# analysis
	# Instead a constant Q transform should be used

	# Alternatively, we could use a ear/cochlear model : logarithmic
	# frequency scale, 4000 logarithmic-spaced bins, quality factors
	# determined from mechanical model, and 50 ms smoothing afterwards
	# for the sensor cell response time. The problem here comes from the
	# implementation: how to do it cleverly ?
	# on top of that, we could add the reponse of the middle ear, which is
	# a roughly band-pass filter centered around 1 kHz (see psychoacoustic
	# models)

	#def analyzelive_cochlear(self, samples, num_channels, lowfreq, maxfreq):
	#	samples -= samples.mean()
	#	
	#	fs = 16000.

	#	[ERBforward, ERBfeedback] = MakeERBFilters(SAMPLING_RATE, num_channels, lowfreq)
	#	filtered_samples = ERBFilterBank(ERBforward, ERBfeedback, samples)

	#	spectrum = (abs(filtered_samples)**2).mean(axis=1)
	#	self.freq = frequencies(SAMPLING_RATE, num_channels, lowfreq)
	#	
	#	return spectrum[::-1], self.freq[::-1]
