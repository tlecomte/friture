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
		
		self.controlWidget = QtGui.QWidget(self)
		self.controlLayout = QtGui.QHBoxLayout(self.controlWidget)
		
		self.comboBox_select = QtGui.QComboBox(self.controlWidget)
		self.comboBox_select.addItem("Levels")
		self.comboBox_select.addItem("Scope")
		self.comboBox_select.addItem("Spectrum")
		self.comboBox_select.addItem("Spectrogram")
		self.comboBox_select.setCurrentIndex(0)
		
		self.settingsButton = QtGui.QPushButton ("Settings", self.controlWidget)
		self.undockButton = QtGui.QPushButton ("Undock", self.controlWidget)
		self.closeButton = QtGui.QPushButton ("Close", self.controlWidget)
		
		self.connect(self.comboBox_select, QtCore.SIGNAL('currentIndexChanged(int)'), self.widget_select)
		self.connect(self.settingsButton, QtCore.SIGNAL('clicked(bool)'), self.settings_slot)
		self.connect(self.undockButton, QtCore.SIGNAL('clicked(bool)'), self.undock_slot)
		self.connect(self.closeButton, QtCore.SIGNAL('clicked(bool)'), self.close_slot)
		
		self.controlLayout.addWidget(self.comboBox_select)
		self.controlLayout.addWidget(self.settingsButton)
		self.controlLayout.addWidget(self.undockButton)
		self.controlLayout.addWidget(self.closeButton)
		
		self.controlWidget.setLayout(self.controlLayout)
		
		self.setTitleBarWidget(self.controlWidget)
		
		self.widget_select(0)
		
		self.connect(self, QtCore.SIGNAL("topLevelChanged(bool)"), self.topLevelChanged_slot)

	# slot
	def widget_select(self, item):
		if item is 0:
			self.audiowidget = Levels_Widget(self)
		elif item is 1:
			self.audiowidget = Scope_Widget(self)
		elif item is 2:
			self.audiowidget = Spectrum_Widget(self)
		else:
			self.audiowidget = Spectrogram_Widget(self, self.logger)
			self.audiowidget.timer.start()
		
		self.audiowidget.set_buffer(self.parent.audiobuffer)
		
		if self.audiowidget.update is not None:
			self.connect(self.parent.display_timer, QtCore.SIGNAL('timeout()'), self.audiowidget.update)
		
		self.setWidget(self.audiowidget)

	# slot
	def settings_slot(self, checked):
		self.widget().settings_called(checked)

	# slot
	def undock_slot(self, checked):
		self.setFloating(True)
		self.setTitleBarWidget(None)

	# slot
	def close_slot(self, checked):
		self.close()
	
	# slot
	def topLevelChanged_slot(self, topLevel):
		if topLevel:
			self.setTitleBarWidget(None)
		else:
			self.setTitleBarWidget(self.controlWidget)
