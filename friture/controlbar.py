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

from PyQt5 import QtGui, QtWidgets


class ControlBar(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.setObjectName("controlBar")

        self.layout = QtWidgets.QHBoxLayout(self)

        self.combobox_select = QtWidgets.QComboBox(self)
        self.combobox_select.addItem("Levels")
        self.combobox_select.addItem("Scope")
        self.combobox_select.addItem("FFT Spectrum")
        self.combobox_select.addItem("2D Spectrogram")
        self.combobox_select.addItem("Octave Spectrum")
        self.combobox_select.addItem("Generator")
        self.combobox_select.addItem("Delay Estimator")
        self.combobox_select.addItem("Long-time levels")
        self.combobox_select.setCurrentIndex(0)
        self.combobox_select.setToolTip("Select the type of audio widget")

        self.settings_button = QtWidgets.QToolButton(self)
        self.settings_button.setToolTip("Customize the audio widget")

        settings_icon = QtGui.QIcon()
        settings_icon.addPixmap(QtGui.QPixmap(":/images-src/dock-settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settings_button.setIcon(settings_icon)

        self.layout.addWidget(self.combobox_select)
        self.layout.addWidget(self.settings_button)
        self.layout.addStretch()

        self.setLayout(self.layout)

        self.setMaximumHeight(24)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
