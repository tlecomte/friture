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

class ControlBar(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self, parent)
		
		self.setObjectName("controlBar")
		
		self.layout = QtGui.QHBoxLayout(self)
		
		self.comboBox_select = QtGui.QComboBox(self)
		self.comboBox_select.addItem("Levels")
		self.comboBox_select.addItem("Scope")
		self.comboBox_select.addItem("FFT Spectrum")
		self.comboBox_select.addItem("2D Spectrogram")
		self.comboBox_select.addItem("Octave Spectrum")
		self.comboBox_select.addItem("Generator")
		self.comboBox_select.addItem("Delay Estimator")
		self.comboBox_select.setCurrentIndex(0)
		self.comboBox_select.setToolTip("Select the type of audio widget")
		
		self.settingsButton = QtGui.QToolButton (self)
		self.settingsButton.setToolTip("Customize the audio widget")
				
		settings_icon = QtGui.QIcon()
		settings_icon.addPixmap(QtGui.QPixmap(":/images-src/dock-settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.settingsButton.setIcon(settings_icon)
		
		self.layout.addWidget(self.comboBox_select)
		self.layout.addWidget(self.settingsButton)
		self.layout.addStretch()
		
		self.setLayout(self.layout)
		
		self.setMaximumHeight(24)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.layout.setSpacing(0)
		self.setStyleSheet(STYLESHEET)
