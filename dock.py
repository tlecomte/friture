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
from levels import Levels_Widget
from spectrum import Spectrum_Widget
from spectrogram import Spectrogram_Widget
from scope import Scope_Widget

class Dock(QtGui.QDockWidget):
	def __init__(self, parent, logger, name):
		QtGui.QDockWidget.__init__(self, name, parent)
		
		self.setObjectName(name)
		
		self.parent = parent
		self.logger = logger
		
		self.widget_select(0)

	# slot
	def widget_select(self, item):
		if item is 0:
			widget = Levels_Widget(self)
		elif item is 1:
			widget = Scope_Widget(self)
		elif item is 2:
			widget = Spectrum_Widget(self)
		else:
			widget = Spectrogram_Widget(self, self.logger)
		
		widget.set_buffer(self.parent.audiobuffer)
		
		if widget.update is not None:
			self.connect(self.parent.display_timer, QtCore.SIGNAL('timeout()'), widget.update)
		
		self.comboBox_select = QtGui.QComboBox(widget)
		self.comboBox_select.addItem("Levels")
		self.comboBox_select.addItem("Scope")
		self.comboBox_select.addItem("Spectrum")
		self.comboBox_select.addItem("Spectrogram")
		self.comboBox_select.setCurrentIndex(item)
		self.connect(self.comboBox_select, QtCore.SIGNAL('currentIndexChanged(int)'), self.widget_select)
		
		self.setWidget(widget)
