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
from numpy import log10, where, linspace, sign
from friture.timeplot import TimePlot
from friture.scope_settings import Scope_Settings_Dialog # settings dialog

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

class Scope_Widget(QtGui.QWidget):
	def __init__(self, parent = None, logger = None):
		QtGui.QWidget.__init__(self, parent)

		self.audiobuffer = None
		
		# store the logger instance
		if logger is None:
		    self.logger = parent.parent.logger
		else:
		    self.logger = logger
		
		self.setObjectName("Scope_Widget")
		self.gridLayout = QtGui.QGridLayout(self)
		self.gridLayout.setObjectName("gridLayout")
		self.PlotZoneUp = TimePlot(self, self.logger)
		self.PlotZoneUp.setObjectName("PlotZoneUp")
		self.gridLayout.addWidget(self.PlotZoneUp, 0, 0, 1, 1)
		
		self.setStyleSheet(STYLESHEET)

		self.settings_dialog = Scope_Settings_Dialog(self, self.logger)

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
		y = floatdata[::-1] - floatdata.mean()
		
		dBscope = False
		if dBscope:
		    dBmin = -50.
		    y = sign(y)*(20*log10(abs(y))).clip(dBmin, 0.)/(-dBmin) + sign(y)*1.
	
		time = linspace(0., len(floatdata)/float(SAMPLING_RATE), len(floatdata))
		self.PlotZoneUp.setdata(time, y)

	# slot
	def settings_called(self, checked):
		self.settings_dialog.show()

	# method
	def saveState(self, settings):
		self.settings_dialog.saveState(settings)
	
	# method
	def restoreState(self, settings):
		self.settings_dialog.restoreState(settings)
