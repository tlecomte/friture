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

from PyQt5 import QtGui, QtCore, QtWidgets
from friture.levels import Levels_Widget
from friture.spectrum import Spectrum_Widget
from friture.spectrogram import Spectrogram_Widget
from friture.octavespectrum import OctaveSpectrum_Widget
from friture.scope import Scope_Widget
from friture.generator import Generator_Widget
from friture.delay_estimator import Delay_Estimator_Widget
from friture.controlbar import ControlBar

class Dock(QtWidgets.QDockWidget):

	def __init__(self, parent, sharedGLWidget, logger, name, type = 0):
		super().__init__(name, parent)
		
		self.setObjectName(name)
		
		self.sharedGLWidget = sharedGLWidget
		self.logger = logger
		
		self.controlBar = ControlBar(self)
				
		self.controlBar.comboBox_select.activated.connect(self.widget_select)
		self.controlBar.settingsButton.clicked.connect(self.settings_slot)

		self.dockwidget = QtWidgets.QWidget(self)
		self.layout = QtWidgets.QVBoxLayout(self.dockwidget)
		self.layout.addWidget(self.controlBar)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.dockwidget.setLayout(self.layout)
		
		self.setWidget(self.dockwidget)
		
		self.audiowidget = None
		self.widget_select(type)

	# note that by default the closeEvent is accepted, no need to do it explicitely
	def closeEvent(self, event):
		self.parent().dockmanager.close_dock(self)

	# slot
	def widget_select(self, item):
		if self.audiowidget is not None:
		    self.audiowidget.close()
		    self.audiowidget.deleteLater()
		
		self.type = item

		if item is 0:
			self.audiowidget = Levels_Widget(self, self.logger)
		elif item is 1:
			self.audiowidget = Scope_Widget(self, self.sharedGLWidget, self.logger)
		elif item is 2:
			self.audiowidget = Spectrum_Widget(self, self.sharedGLWidget, self.logger)
		elif item is 3:
			self.audiowidget = Spectrogram_Widget(self, self.parent().audiobackend, self.logger)
		elif item is 4:
			self.audiowidget = OctaveSpectrum_Widget(self, self.logger)
		elif item is 5:
			self.audiowidget = Generator_Widget(self, self.parent().audiobackend, self.logger)
		elif item is 6:
			self.audiowidget = Delay_Estimator_Widget(self, self.logger)
		
		self.audiowidget.set_buffer(self.parent().audiobuffer)

		self.layout.addWidget(self.audiowidget)
		
		self.controlBar.comboBox_select.setCurrentIndex(item)

	def update(self):
		if self.audiowidget is not None:
			self.audiowidget.update()

	def pause(self):
		if self.audiowidget is not None:
			self.audiowidget.pause()

	def restart(self):
		if self.audiowidget is not None:
			self.audiowidget.restart()

	# slot
	def settings_slot(self, checked):
		self.audiowidget.settings_called(checked)

	# method
	def saveState(self, settings):
		settings.setValue("type", self.type)
		self.audiowidget.saveState(settings)
	
	# method
	def restoreState(self, settings):
		widgetType = settings.value("type", 0)
		self.widget_select(widgetType)
		self.audiowidget.restoreState(settings)
