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

from PyQt4 import QtGui, QtCore
from numpy import log10, where, linspace
from histplot import HistPlot
import audioproc # audio processing class
import octavespectrum_settings # settings dialog
from cochlear import *

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
SAMPLING_RATE = 44100

STYLESHEET = """
QwtPlotCanvas {
	border: 1px solid gray;
	border-radius: 2px;
	background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
	stop: 0 #E0E0E0, stop: 0.5 #FFFFFF);
}
"""

# shared with octavespectrum_settings.py
DEFAULT_SPEC_MIN = -140
DEFAULT_SPEC_MAX = 0
DEFAULT_WEIGHTING = 1 #A

class OctaveSpectrum_Widget(QtGui.QWidget):
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
		self.PlotZoneSpect = HistPlot(self, self.logger)
		self.PlotZoneSpect.setObjectName("PlotZoneSpect")
		self.gridLayout.addWidget(self.PlotZoneSpect, 0, 0, 1, 1)

		self.setStyleSheet(STYLESHEET)
		
		# initialize the class instance that will do the fft
		self.proc = audioproc.audioproc(self.logger)
		
		self.spec_min = DEFAULT_SPEC_MIN
		self.spec_max = DEFAULT_SPEC_MAX
		self.weighting = DEFAULT_WEIGHTING
		
		BandsPerOctave = 1
		Nbands = 7*BandsPerOctave
		[self.b, self.a, self.fi, self.flow, self.fhigh] = octave_filters(Nbands, BandsPerOctave)
		
		# initialize the settings dialog
		self.settings_dialog = octavespectrum_settings.OctaveSpectrum_Settings_Dialog(self, self.logger)

	# method
	def set_buffer(self, buffer):
		self.audiobuffer = buffer

	# method
	def update(self):
		if not self.isVisible():
		    return
		
		#time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000.
		time = 0.135 #FAST setting for a sound level meter
		floatdata = self.audiobuffer.data(time*SAMPLING_RATE)
		y = octave_filter_bank(self.b, self.a, floatdata)
		
		sp = (y**2).mean(axis=1)
		freq = self.fi
		
		# taken from http://www.cdc.gov/niosh/docs/98-126/chap4.html#41
		# which takes it in turn from ANSI standards
		A = [-16.1, -8.6, -3.2, 0., 1.2, 1.0, -1.1]
		B = [-4.2, -1.3, -0.3, 0., -0.1, -0.7, -2.9]
		C = [-0.2, 0., 0., 0., -0.2, -0.8, -3.0]
		
		if self.weighting is 0:
			w = 0.
		elif self.weighting is 1:
			w = A
		elif self.weighting is 2:
			w = B
		else:
			w = C
		
		epsilon = 1e-30
		db_spectrogram = 20*log10(sp + epsilon) + w
		self.PlotZoneSpect.setdata(self.flow, self.fhigh, db_spectrogram)

	def setmin(self, value):
		self.spec_min = value
		self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)
	
	def setmax(self, value):
		self.spec_max = value
		self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)

	def setweighting(self, weighting):
		self.weighting = weighting
		self.PlotZoneSpect.setweighting(weighting)

	def settings_called(self, checked):
		self.settings_dialog.show()
	
	def saveState(self, settings):
		self.settings_dialog.saveState(settings)

	def restoreState(self, settings):
		self.settings_dialog.restoreState(settings)
