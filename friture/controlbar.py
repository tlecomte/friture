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


class ControlBar(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.setObjectName("controlBar")

        self.layout = QtWidgets.QHBoxLayout(self)

        self.comboBox_select = QtWidgets.QComboBox(self)
        self.comboBox_select.addItem("Levels")
        self.comboBox_select.addItem("Scope")
        self.comboBox_select.addItem("FFT Spectrum")
        self.comboBox_select.addItem("2D Spectrogram")
        self.comboBox_select.addItem("Octave Spectrum")
        self.comboBox_select.addItem("Generator")
        self.comboBox_select.addItem("Delay Estimator")
        self.comboBox_select.setCurrentIndex(0)
        self.comboBox_select.setToolTip("Select the type of audio widget")

        self.settingsButton = QtWidgets.QToolButton(self)
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
