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
from Ui_spectrum import Ui_Spectrum_Widget
import audioproc # audio processing class
import spectrum_settings # settings dialog

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
SAMPLING_RATE = 44100

STYLESHEET = """
QwtPlotCanvas {
	border: 1px solid gray;
	border-radius: 2px;
	background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
	stop: 0 #AAAAAA, stop: 0.3 #FFFFFF);
}
"""

class Spectrum_Widget(QtGui.QWidget, Ui_Spectrum_Widget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self, parent)
		Ui_Spectrum_Widget.__init__(self)

		# store the logger instance
		# FIXME
		#self.logger = parent.parent().logger
		self.logger = None

		self.audiobuffer = None

		# Setup the user interface
		self.setupUi(self)
		
		self.setStyleSheet(STYLESHEET)
		
		# initialize the class instance that will do the fft
		self.proc = audioproc.audioproc()
		
		self.maxfreq = SAMPLING_RATE/2
		self.minfreq = 0
		self.fft_size = 256
		
		# initialize the settings dialog
		self.settings_dialog = spectrum_settings.Spectrum_Settings_Dialog(self, self.logger)

		# display the settings dialog
		self.connect(self.pushButtonSettings, QtCore.SIGNAL('clicked(bool)'), self.settings_called)

	# method
	def set_buffer(self, buffer):
		self.audiobuffer = buffer

	# method
	def update(self):
		if not self.isVisible():
		    return
		
		floatdata = self.audiobuffer.data(self.fft_size)
		sp, freq = self.proc.analyzelive(floatdata, self.fft_size, self.maxfreq)
		#sp, freq = self.proc.analyzelive_cochlear(floatdata, 50, minfreq, maxfreq)
		# scale the db spectrum from [- spec_range db ... 0 db] > [0..1]
		epsilon = 1e-30
		db_spectrogram = 20*log10(sp + epsilon)
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
		# FIXME should change the plot range
		self.spec_min = value
	
	def setmax(self, value):
		# FIXME should change the plot range
		self.spec_max = value

	def settings_called(self, checked):
		self.settings_dialog.show()
	
	def saveState(self, settings):
		self.settings_dialog.saveState(settings)

	def restoreState(self, settings):
		self.settings_dialog.restoreState(settings)
