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
from Ui_levels import Ui_Levels_Widget
import levels_settings # settings dialog

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
SAMPLING_RATE = 44100

class Levels_Widget(QtGui.QWidget, Ui_Levels_Widget):
	def __init__(self, parent = None, logger = None):
		QtGui.QWidget.__init__(self, parent)
		Ui_Levels_Widget.__init__(self)

		# store the logger instance
		if logger is None:
		    self.logger = parent.parent.logger
		else:
		    self.logger = logger

		self.audiobuffer = None
		
		# Setup the user interface
		self.setupUi(self)
		
		# initialize the settings dialog
		self.settings_dialog = levels_settings.Levels_Settings_Dialog(self, self.logger)

	# method
	def set_buffer(self, buffer):
		self.audiobuffer = buffer

	# method
	def update(self):
		if not self.isVisible():
			return
		
		# for slower response, we need to implement a low-pass filter here. 
		
		time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000.
		floatdata = self.audiobuffer.data(time*SAMPLING_RATE)
		
		level_rms = 10*log10((floatdata**2).sum()/len(floatdata)*2. + 0*1e-80) #*2. to get 0dB for a sine wave
		level_max = 20*log10(abs(floatdata).max() + 0*1e-80)
		self.label_rms.setText("%.01f" % level_rms)
		self.label_peak.setText("%.01f" % level_max)
		self.meter.setValue(0, level_rms)
		self.meter.setValue(1, level_max)

	# slot
	def settings_called(self, checked):
		self.settings_dialog.show()

	# method
	def saveState(self, settings):
		self.settings_dialog.saveState(settings)
	
	# method
	def restoreState(self, settings):
		self.settings_dialog.restoreState(settings)
