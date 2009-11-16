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
SAMPLING_RATE = 44100

class audioproc():
	def __init__(self):
		self.freq = linspace(0, SAMPLING_RATE/2, 10)

	def analyzelive(self, samples, fft_size, maxfreq):
		#samples *= window
		# first we remove as much points as possible
		decimation = SAMPLING_RATE/2 / (2*maxfreq)
		decimation = 2**(floor(log2(decimation)))
		
		samples.shape = len(samples)/decimation, decimation
		#the full way
		#samples = samples.mean(axis=1)
		#the simplest way
		samples = samples[:,0]
		
		#uncomment the following to disable the decimation altogether
		#decimation = 1
		
		fft = rfft(samples)
		spectrum = abs(fft) / float(fft_size/decimation)

		if len(self.freq) <> fft_size/2/decimation + 1 :
			self.freq = linspace(0, SAMPLING_RATE/2/decimation, fft_size/2/decimation + 1)
		return spectrum, self.freq

# above is done a FFT of the signal. This is ok for linear frequency scale, but
# not satisfying for logarithmic scale, which is much more adapted to voice or music
# analysis
# Instead a constant Q transform should be used
