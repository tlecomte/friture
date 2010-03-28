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
from Ui_scope import Ui_Scope_Widget

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
SAMPLING_RATE = 44100

class Scope_Widget(QtGui.QWidget, Ui_Scope_Widget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)
		Ui_Scope_Widget.__init__(self)
		
		self.audiobuffer = None
		
		# Setup the user interface
		self.setupUi(self)

	# method
	def set_buffer(self, buffer):
		self.audiobuffer = buffer

	# method
	def update(self):
		if not self.isVisible():
			return

		time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000.
		#basic trigger capability on leading edge
		floatdata = self.audiobuffer.data(time*SAMPLING_RATE)
		max = floatdata.max()
		trigger_level = max*2./3.
		trigger_pos = where((floatdata[:-1] < trigger_level)*(floatdata[1:] >= trigger_level))[0]
		if len(trigger_pos) > 0:
			shift = time*SAMPLING_RATE - trigger_pos[0]
		else:
			shift = 0
		floatdata = self.audiobuffer.data(time*SAMPLING_RATE + shift)
		floatdata = floatdata[0 : time*SAMPLING_RATE]
		y = floatdata - floatdata.mean()
		
		dBscope = False
		if dBscope:
		    dBmin = -40.
		    y = sign(y)*(20*log10(abs(y))).clip(dBmin, 0.)/(-dBmin) + sign(y)*1.
	
		time = linspace(0., len(floatdata)/float(SAMPLING_RATE), len(floatdata))
		self.PlotZoneUp.setdata(time, y)

	# method
	def saveState(self, settings):
		return
	
	# method
	def restoreState(self, settings):
		return
