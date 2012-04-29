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
from friture.levels import Levels_Widget
from friture.spectrum import Spectrum_Widget
from friture.spectrogram import Spectrogram_Widget
from friture.octavespectrum import OctaveSpectrum_Widget
from friture.scope import Scope_Widget
from friture.generator import Generator_Widget
from friture.delay_estimator import Delay_Estimator_Widget
from friture.controlbar import ControlBar

class CentralWidget(QtGui.QWidget):
	def __init__(self, parent, logger, name, type = 0):
		QtGui.QWidget.__init__(self, parent)
		
		self.setObjectName(name)
		
		self.parent = parent
		self.logger = logger
		
		self.controlBar = ControlBar(self)
				
		self.connect(self.controlBar.comboBox_select, QtCore.SIGNAL('activated(int)'), self.widget_select)
		self.connect(self.controlBar.settingsButton, QtCore.SIGNAL('clicked(bool)'), self.settings_slot)
		
		self.label = QtGui.QLabel(self)
		self.label.setText(" Central dock ") # spaces before and after for nicer alignment
		self.controlBar.layout.insertWidget(0, self.label)
		
		self.layout = QtGui.QVBoxLayout(self)
		self.layout.addWidget(self.controlBar)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.layout)
		
		self.audiowidget = None
		self.widget_select(type)

	# slot
	def widget_select(self, item):
		if self.audiowidget is not None:
		    self.audiowidget.close()
		    self.audiowidget.deleteLater()
		
		self.type = item
		
		if item is 0:
			self.audiowidget = Levels_Widget(self, self.logger)
		elif item is 1:
			self.audiowidget = Scope_Widget(self, self.logger)
		elif item is 2:
			self.audiowidget = Spectrum_Widget(self, self.logger)
		elif item is 3:
			self.audiowidget = Spectrogram_Widget(self, self.logger)
			self.audiowidget.timer.start()
		elif item is 4:
			self.audiowidget = OctaveSpectrum_Widget(self, self.logger)
		elif item is 5:
			self.audiowidget = Generator_Widget(self, self.parent.parent().audiobackend, self.logger)
		elif item is 6:
			self.audiowidget = Delay_Estimator_Widget(self, self.logger)

		self.audiowidget.set_buffer(self.parent.parent().audiobuffer)
		
		if self.audiowidget.update is not None:
			self.connect(self.parent.parent().display_timer, QtCore.SIGNAL('timeout()'), self.audiowidget.update)

		self.layout.addWidget(self.audiowidget)
		
		self.controlBar.comboBox_select.setCurrentIndex(item)

	def custom_timer_start(self):
		try:
			self.audiowidget.timer.start()
		except:
			pass

	def custom_timer_stop(self):
		try:
			self.audiowidget.timer.stop()
		except:
			pass

	# slot
	def settings_slot(self, checked):
		self.audiowidget.settings_called(checked)

	# method
	def saveState(self, settings):
		settings.setValue("type", self.type)
		self.audiowidget.saveState(settings)
	
	# method
	def restoreState(self, settings):
		(type, ok) = settings.value("type", 2).toInt()
		self.widget_select(type)
		self.audiowidget.restoreState(settings)
