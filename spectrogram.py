#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

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

from PyQt4 import QtGui
from numpy import log10, where, linspace
from Ui_spectrogram import Ui_Spectrogram_Widget
import audioproc # audio processing class

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
SAMPLING_RATE = 44100

class Spectrogram_Widget(QtGui.QWidget, Ui_Spectrogram_Widget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)
		Ui_Spectrogram_Widget.__init__(self)
		
		# Setup the user interface
		self.setupUi(self)
		
		# initialize the class instance that will do the fft
		self.proc = audioproc.audioproc()

		self.maxfreq = SAMPLING_RATE/2
		self.minfreq = 0
		self.fft_size = 256
		self.spec_min = -100.
		self.spec_max = -20.

	# method
	def update(self, audiobuffer):
		# FIXME We should allow here for more intelligent transforms, especially when the log freq scale is selected
		floatdata = audiobuffer.data(self.fft_size)
		sp, freq = self.proc.analyzelive(floatdata, self.fft_size, self.maxfreq)
		# scale the db spectrum from [- spec_range db ... 0 db] > [0..1]
		epsilon = 1e-30
		db_spectrogram = 20*log10(sp + epsilon)
		norm_spectrogram = (db_spectrogram.clip(min = self.spec_min, max = self.spec_max) - self.spec_min)/(self.spec_max - self.spec_min)
		
		self.PlotZoneImage.addData(freq, norm_spectrogram)

	def setminfreq(self, freq):
		self.minfreq = freq
		self.PlotZoneImage.setfreqrange(self.minfreq, self.maxfreq)

	def setmaxfreq(self, freq):
		self.maxfreq = freq
		self.PlotZoneImage.setfreqrange(self.minfreq, self.maxfreq)
	
	def setfftsize(self, fft_size):
		self.fft_size = fft_size

	def setmin(self, value):
		self.spec_min = value
	
	def setmax(self, value):
		self.spec_max = value
