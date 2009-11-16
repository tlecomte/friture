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

import numpy
SAMPLING_RATE = 44100

class audioproc():
	def __init__(self):
		self.freq = numpy.linspace(0, SAMPLING_RATE/2, 10)

	def analyzelive(self, samples, fft_size):
		#samples *= window
		fft = numpy.fft.rfft(samples)
		spectrum = numpy.abs(fft) / float(fft_size)
		if len(self.freq) <> len(spectrum):
			self.freq = numpy.linspace(0, SAMPLING_RATE/2, len(spectrum))
		return spectrum, self.freq

# above is done a FFT of the signal. This is ok for linear frequency scale, but
# not satisfying for logarithmic scale, which is much more adapted to voice or music
# analysis
# Instead a constant Q transform should be used
