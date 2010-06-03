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

STYLESHEET = """
"""

#QWidget#controlWidget, QWidget#floatingcontrolWidget {
#border: none;
#background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#stop: 0 #a6a6a6, stop: 0.08 #7f7f7f,
#stop: 0.39999 #717171, stop: 0.4 #626262,
#stop: 0.9 #4c4c4c, stop: 1 #333333);
#/* padding: 0px; */

#}

#QComboBox {
#color: white;
#border-style: solid;
#border-color: black;
#border-top-width: 0px;
#border-bottom-width: 0px;
#border-left-width: 0px;
#border-right-width: 1px;
#background-color: rgba(255,255,255,10%);
#min-height:20px;
#padding: 1px 10px 1px 3px;
#}

#QComboBox::drop-down {
#border: none;
#subcontrol-position: center right;
#subcontrol-origin: padding;
#/* border-left-width: 1px;*/
#/* border-left-color: darkgray;*/
#/* border-left-style: solid;*/ /* just a single line */
#/* border-top-right-radius: 3px;*/ /* same radius as the QComboBox */
#/* border-bottom-right-radius: 3px;*/
#}

#QComboBox::down-arrow {
#image: url(:/dock-close.svg);
#width: 10px;
#height: 10px;
#}

#QComboBox::down-arrow:on { /* shift the arrow when popup is open */
#top: 1px;
#left: 1px;
#}

#QComboBox:hover {
#background-color: rgba(255,255,255,20%);
#}

#QComboBox:open {
#background-color: rgba(255,255,255,30%);
#}

#QToolButton {
#background-color: rgba(255,255,255,10%);
#/* qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#stop: 0 #a6a6a6, stop: 0.08 #7f7f7f,
#stop: 0.39999 #717171, stop: 0.4 #626262,
#stop: 0.9 #4c4c4c, stop: 1 #333333); */
#border-style: solid;
#border-color: black;
#border-top-width: 0px;
#border-bottom-width: 0px;
#border-left-width: 1px;
#border-right-width: 0px;
#/*border: none;*/
#/*padding: 0px;*/
#/*margin: 0px;*/
#/*icon-size: 10px;*/
#/*min-width:20px;*/
#min-height:20px;
#max-height:20px;
#/*text-align: center right;*/
#}

#QToolButton:hover {
#background-color: rgba(255,255,255,20%);
#}

#QToolButton:pressed {
#background-color: rgba(255,255,255,30%);
#}
#"""

class Dock(QtGui.QDockWidget):
	def __init__(self, parent, logger, name, type = 0):
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
		
		self.settingsButton = QtGui.QToolButton (self.controlWidget)
		self.undockButton = QtGui.QToolButton (self.controlWidget)
		self.closeButton = QtGui.QToolButton (self.controlWidget)
		
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/dock-close.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.closeButton.setIcon(icon)
		
		settings_icon = QtGui.QIcon()
		settings_icon.addPixmap(QtGui.QPixmap(":/dock-settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.settingsButton.setIcon(settings_icon)
		
		undock_icon = QtGui.QIcon()
		undock_icon.addPixmap(QtGui.QPixmap(":/dock-undock.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.undockButton.setIcon(undock_icon)
		
		self.connect(self.comboBox_select, QtCore.SIGNAL('activated(int)'), self.widget_select)
		self.connect(self.settingsButton, QtCore.SIGNAL('clicked(bool)'), self.settings_slot)
		self.connect(self.undockButton, QtCore.SIGNAL('clicked(bool)'), self.undock_slot)
		self.connect(self.closeButton, QtCore.SIGNAL('clicked(bool)'), self.close_slot)
		
		self.controlLayout.addWidget(self.comboBox_select)
		self.controlLayout.addStretch()
		self.controlLayout.addWidget(self.settingsButton)
		self.controlLayout.addWidget(self.undockButton)
		self.controlLayout.addWidget(self.closeButton)
		
		self.controlWidget.setLayout(self.controlLayout)
		
		#self.setTitleBarWidget(self.controlWidget)
		
		self.connect(self, QtCore.SIGNAL("topLevelChanged(bool)"), self.topLevelChanged_slot)
		
		self.floatingcontrolWidget = QtGui.QWidget(self)
		self.floatingcontrolLayout = QtGui.QHBoxLayout(self.floatingcontrolWidget)
		
		self.floatingcomboBox_select = QtGui.QComboBox(self.floatingcontrolWidget)
		self.floatingcomboBox_select.addItem("Levels")
		self.floatingcomboBox_select.addItem("Scope")
		self.floatingcomboBox_select.addItem("Spectrum")
		self.floatingcomboBox_select.addItem("Spectrogram")
		self.floatingcomboBox_select.setCurrentIndex(0)
		
		self.floatingsettingsButton = QtGui.QToolButton (self.floatingcontrolWidget)
		#self.floatingdockButton = QtGui.QToolButton (self.floatingcontrolWidget)
		
		#dock_icon = QtGui.QIcon()
		#dock_icon.addPixmap(QtGui.QPixmap(":/dock-dock.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		#self.floatingdockButton.setIcon(dock_icon)
		
		self.floatingsettingsButton.setIcon(settings_icon)
		
		self.connect(self.floatingcomboBox_select, QtCore.SIGNAL('activated(int)'), self.widget_select)
		self.connect(self.floatingsettingsButton, QtCore.SIGNAL('clicked(bool)'), self.settings_slot)
		#self.connect(self.floatingdockButton, QtCore.SIGNAL('clicked(bool)'), self.dock_slot)
		
		self.floatingcontrolLayout.addWidget(self.floatingcomboBox_select)
		self.floatingcontrolLayout.addStretch()
		self.floatingcontrolLayout.addWidget(self.floatingsettingsButton)
		#self.floatingcontrolLayout.addWidget(self.floatingdockButton)
		
		self.dockwidget = QtGui.QWidget(self)
		self.floatingLayout = QtGui.QVBoxLayout(self.dockwidget)
		self.floatingLayout.addWidget(self.floatingcontrolWidget)
		self.dockwidget.setLayout(self.floatingLayout)
		
		#self.floatingcontrolWidget.hide()
		self.controlWidget.hide()
		
		self.floatingLayout.setContentsMargins(0, 0, 0, 0)
		self.floatingcontrolLayout.setContentsMargins(0, 0, 0, 0)
		self.controlLayout.setContentsMargins(0, 0, 0, 0)
		self.controlLayout.setSpacing(0)
		self.floatingcontrolLayout.setSpacing(0)
		self.controlWidget.setObjectName("controlWidget")
		self.controlWidget.setMaximumHeight(24)
		self.floatingcontrolWidget.setObjectName("floatingcontrolWidget")
		self.floatingcontrolWidget.setMaximumHeight(24)
		self.setStyleSheet(STYLESHEET)
		
		self.setWidget(self.dockwidget)
		
		self.audiowidget = None
		self.widget_select(type)

	# slot
	def widget_select(self, item):
		if self.audiowidget is not None:
		    self.audiowidget.close()
		
		self.type = item
		
		if item is 0:
			self.audiowidget = Levels_Widget(self, self.logger)
		elif item is 1:
			self.audiowidget = Scope_Widget(self, self.logger)
		elif item is 2:
			self.audiowidget = Spectrum_Widget(self, self.logger)
		else:
			self.audiowidget = Spectrogram_Widget(self, self.logger)
			self.audiowidget.timer.start()
		
		self.audiowidget.set_buffer(self.parent.audiobuffer)
		
		if self.audiowidget.update is not None:
			self.connect(self.parent.display_timer, QtCore.SIGNAL('timeout()'), self.audiowidget.update)

		self.floatingLayout.addWidget(self.audiowidget)
		
		self.floatingcomboBox_select.setCurrentIndex(item)
		self.comboBox_select.setCurrentIndex(item)

	# slot
	def settings_slot(self, checked):
		self.audiowidget.settings_called(checked)

	# slot
	def undock_slot(self, checked):
		self.setFloating(True)
	
	# slot
	def dock_slot(self, checked):
		self.setFloating(False)

	# slot
	def close_slot(self, checked):
		self.close()
	
	# slot
	def topLevelChanged_slot(self, topLevel):
		#if topLevel:
		self.setTitleBarWidget(None)
		self.floatingcontrolWidget.show()

		#else:
			#self.setTitleBarWidget(self.controlWidget)
			#self.floatingcontrolWidget.hide()

	# method
	def saveState(self, settings):
		settings.setValue("type", self.type)
		self.audiowidget.saveState(settings)
	
	# method
	def restoreState(self, settings):
		(type, ok) = settings.value("type", 0).toInt()
		self.widget_select(type)
		self.audiowidget.restoreState(settings)
