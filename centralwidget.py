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

class CentralWidget(QtGui.QWidget):
	def __init__(self, parent, logger, name, type = 0):
		QtGui.QWidget.__init__(self, parent)
		
		self.setObjectName(name)
		
		self.parent = parent
		self.logger = logger
		
		self.floatingcontrolWidget = QtGui.QWidget(self)
		self.floatingcontrolLayout = QtGui.QHBoxLayout(self.floatingcontrolWidget)
		
		self.floatingcomboBox_select = QtGui.QComboBox(self.floatingcontrolWidget)
		self.floatingcomboBox_select.addItem("Levels")
		self.floatingcomboBox_select.addItem("Scope")
		self.floatingcomboBox_select.addItem("Spectrum")
		self.floatingcomboBox_select.addItem("Spectrogram")
		self.floatingcomboBox_select.setCurrentIndex(0)
		
		self.floatingsettingsButton = QtGui.QToolButton (self.floatingcontrolWidget)
		
		settings_icon = QtGui.QIcon()
		settings_icon.addPixmap(QtGui.QPixmap(":/dock-settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.floatingsettingsButton.setIcon(settings_icon)
		
		self.connect(self.floatingcomboBox_select, QtCore.SIGNAL('activated(int)'), self.widget_select)
		self.connect(self.floatingsettingsButton, QtCore.SIGNAL('clicked(bool)'), self.settings_slot)
		
		self.floatingcontrolLayout.addWidget(self.floatingcomboBox_select)
		self.floatingcontrolLayout.addWidget(self.floatingsettingsButton)
		self.floatingcontrolLayout.addStretch()
		
		self.floatingLayout = QtGui.QVBoxLayout(self)
		self.floatingLayout.addWidget(self.floatingcontrolWidget)
		#self.setLayout(self.floatingLayout)
		
		self.floatingLayout.setContentsMargins(0, 0, 0, 0)
		self.floatingcontrolLayout.setContentsMargins(0, 0, 0, 0)
		self.floatingcontrolLayout.setSpacing(0)
		self.floatingcontrolWidget.setObjectName("floatingcontrolWidget")
		self.floatingcontrolWidget.setMaximumHeight(24)
		self.setStyleSheet(STYLESHEET)
		
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
		
		self.audiowidget.set_buffer(self.parent.parent().audiobuffer)
		
		if self.audiowidget.update is not None:
			self.connect(self.parent.parent().display_timer, QtCore.SIGNAL('timeout()'), self.audiowidget.update)

		self.floatingLayout.addWidget(self.audiowidget)
		
		self.floatingcomboBox_select.setCurrentIndex(item)

	# slot
	def settings_slot(self, checked):
		self.audiowidget.settings_called(checked)

	# method
	def saveState(self, settings):
		settings.setValue("type", self.type)
		self.audiowidget.saveState(settings)
	
	# method
	def restoreState(self, settings):
		(type, ok) = settings.value("type", 0).toInt()
		self.widget_select(type)
		self.audiowidget.restoreState(settings)
