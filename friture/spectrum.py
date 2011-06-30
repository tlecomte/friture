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
from numpy import log10
from friture.spectplot import SpectPlot
from friture.audioproc import audioproc # audio processing class
from friture.spectrum_settings import Spectrum_Settings_Dialog # settings dialog

from friture.qwtopenglplot import GLPlotWidget

STYLESHEET = """
QwtPlotCanvas {
	border: 1px solid gray;
	border-radius: 2px;
	background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
	stop: 0 #E0E0E0, stop: 0.5 #FFFFFF);
}
"""

# shared with spectrum_settings.py
SAMPLING_RATE = 44100
DEFAULT_FFT_SIZE = 7 #4096 points
DEFAULT_FREQ_SCALE = 1 #log10
DEFAULT_MAXFREQ = 20000
DEFAULT_MINFREQ = 20
DEFAULT_SPEC_MIN = -100
DEFAULT_SPEC_MAX = -20
DEFAULT_WEIGHTING = 1 #A

class Spectrum_Widget(QtGui.QWidget):
	def __init__(self, parent, logger = None):
		QtGui.QWidget.__init__(self, parent)

		# store the logger instance
		if logger is None:
		    self.logger = parent.parent.logger
		else:
		    self.logger = logger

		self.audiobuffer = None

		self.setObjectName("Spectrum_Widget")
		self.gridLayout = QtGui.QGridLayout(self)
		self.gridLayout.setObjectName("gridLayout")
		#self.PlotZoneSpect = SpectPlot(self, self.logger)
  		self.PlotZoneSpect = GLPlotWidget(self, self.logger)
		self.PlotZoneSpect.setObjectName("PlotZoneSpect")
		self.gridLayout.addWidget(self.PlotZoneSpect, 0, 0, 1, 1)

		self.setStyleSheet(STYLESHEET)
		
		# initialize the class instance that will do the fft
		self.proc = audioproc(self.logger)
		
		self.maxfreq = DEFAULT_MAXFREQ
		self.minfreq = DEFAULT_MINFREQ
		self.fft_size = 2**DEFAULT_FFT_SIZE*32
		self.spec_min = DEFAULT_SPEC_MIN
		self.spec_max = DEFAULT_SPEC_MAX
		self.weighting = DEFAULT_WEIGHTING
		self.dual_channels = False
		
		self.PlotZoneSpect.setlogfreqscale() #DEFAULT_FREQ_SCALE = 1 #log10
		self.PlotZoneSpect.setfreqrange(self.minfreq, self.maxfreq)
		self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)
		self.PlotZoneSpect.setweighting(self.weighting)
		self.PlotZoneSpect.set_peaks_enabled(True)
		self.PlotZoneSpect.set_baseline_displayUnits(0.)
		
		# initialize the settings dialog
		self.settings_dialog = Spectrum_Settings_Dialog(self, self.logger)

	# method
	def set_buffer(self, buffer):
		self.audiobuffer = buffer

	# method
	def update(self):
		if not self.isVisible():
		    return
		
		floatdata = self.audiobuffer.data(self.fft_size)

		# first channel
		sp1, freq, A, B, C = self.proc.analyzelive(floatdata[0,:], self.fft_size, self.maxfreq)

		if self.dual_channels and floatdata.shape[0] > 1:
			# second channel for comparison
			sp2, freq, A, B, C  = self.proc.analyzelive(floatdata[1,:], self.fft_size, self.maxfreq)   

			floatdata_delayed = self.audiobuffer.data_delayed(self.fft_size)
			sp1, freq, A, B, C  = self.proc.analyzelive(floatdata_delayed[0,:], self.fft_size, self.maxfreq)   

		#sp, freq = self.proc.analyzelive_cochlear(floatdata, 50, minfreq, maxfreq)
		# scale the db spectrum from [- spec_range db ... 0 db] > [0..1]
		#print freq[len(freq)/6], A[len(freq)/6]
		epsilon = 1e-30
		
		if self.weighting is 0:
			w = 0.
		elif self.weighting is 1:
			w = A
		elif self.weighting is 2:
			w = B
		else:
			w = C

	           # the log operation and the weighting could be deffered
	           # to the post-weedening !		
		if self.dual_channels and floatdata.shape[0] > 1:
			db_spectrogram = 20*log10(sp2 + epsilon) - 20*log10(sp1 + epsilon)
		else:
			db_spectrogram = 20*log10(sp1 + epsilon) + w

		self.PlotZoneSpect.setdata(freq, db_spectrogram)

	def setminfreq(self, freq):
		self.minfreq = freq
		self.PlotZoneSpect.setfreqrange(self.minfreq, self.maxfreq)

	def setmaxfreq(self, freq):
		self.maxfreq = freq
		self.PlotZoneSpect.setfreqrange(self.minfreq, self.maxfreq)

	def setfftsize(self, fft_size):
		self.fft_size = fft_size

	def setmin(self, value):
		self.spec_min = value
		self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)
	
	def setmax(self, value):
		self.spec_max = value
		self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)

	def setweighting(self, weighting):
		self.weighting = weighting
		self.PlotZoneSpect.setweighting(weighting)

	def setdualchannels(self, dual_enabled):
		self.dual_channels = dual_enabled
		if dual_enabled:
			self.PlotZoneSpect.set_peaks_enabled(False)
			self.PlotZoneSpect.set_baseline_dataUnits(0.)
		else:
			self.PlotZoneSpect.set_peaks_enabled(True)
			self.PlotZoneSpect.set_baseline_displayUnits(0.)

	def settings_called(self, checked):
		self.settings_dialog.show()
	
	def saveState(self, settings):
		self.settings_dialog.saveState(settings)

	def restoreState(self, settings):
		self.settings_dialog.restoreState(settings)
