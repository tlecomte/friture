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

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
SAMPLING_RATE = 44100

class Levels_Widget(QtGui.QWidget, Ui_Levels_Widget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)
		Ui_Levels_Widget.__init__(self)
		
		# Setup the user interface
		self.setupUi(self)

	# method
	def update(self, audiobuffer):
		if not self.isVisible():
			return
		
		time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000.
		floatdata = audiobuffer.data(time*SAMPLING_RATE)
		
		level_rms = 10*log10((floatdata**2).sum()/len(floatdata)*2. + 0*1e-80) #*2. to get 0dB for a sine wave
		level_max = 20*log10(abs(floatdata).max() + 0*1e-80)
		self.label_rms.setText("%.01f" % level_rms)
		self.label_peak.setText("%.01f" % level_max)
		self.meter.setValue(0, level_rms)
		self.meter.setValue(1, level_max)
