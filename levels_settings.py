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

class Levels_Settings_Dialog(QtGui.QDialog):
	def __init__(self, parent, logger):
		QtGui.QDialog.__init__(self, parent)
		
		self.parent = parent
		self.logger = logger
		
		self.setWindowTitle("Levels settings")
		
		self.formLayout = QtGui.QFormLayout(self)
		
		#self.doubleSpinBox_timerange = QtGui.QDoubleSpinBox(self)
		#self.doubleSpinBox_timerange.setDecimals(1)
		#self.doubleSpinBox_timerange.setMinimum(0.1)
		#self.doubleSpinBox_timerange.setMaximum(1000.0)
		#self.doubleSpinBox_timerange.setProperty("value", DEFAULT_TIMERANGE)
		#self.doubleSpinBox_timerange.setObjectName("doubleSpinBox_timerange")
		#self.doubleSpinBox_timerange.setSuffix(" s")

		#self.formLayout.addRow("Time range:", self.doubleSpinBox_timerange)
		self.formLayout.addRow("No settings for the levels.", None)
		
		self.setLayout(self.formLayout)

		#self.connect(self.doubleSpinBox_timerange, QtCore.SIGNAL('valueChanged(double)'), self.parent.timerangechanged)

	# method
	def saveState(self, settings):
		#settings.setValue("timeRange", self.doubleSpinBox_timerange.value())
		return

	# method
	def restoreState(self, settings):
		#(timeRange, ok) = settings.value("timeRange", DEFAULT_TIMERANGE).toDouble()
		#self.doubleSpinBox_timerange.setValue(timeRange)
		return
