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

from PyQt5 import QtWidgets
from friture.audiobackend import SAMPLING_RATE

DEFAULT_MAXTIME = 600
#DEFAULT_MINTIME = 20
DEFAULT_LEVEL_MIN = -70
DEFAULT_LEVEL_MAX = -20
DEFAULT_RESPONSE_TIME = 20
#DEFAULT_RESPONSE_TIME_INDEX = 0


class LongLevels_Settings_Dialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Long levels settings")

        self.formLayout = QtWidgets.QFormLayout(self)

        self.spinBox_specmin = QtWidgets.QSpinBox(self)
        self.spinBox_specmin.setKeyboardTracking(False)
        self.spinBox_specmin.setMinimum(-200)
        self.spinBox_specmin.setMaximum(200)
        self.spinBox_specmin.setProperty("value", DEFAULT_LEVEL_MIN)
        self.spinBox_specmin.setObjectName("longlevels_specmin")
        self.spinBox_specmin.setSuffix(" dB")

        self.spinBox_specmax = QtWidgets.QSpinBox(self)
        self.spinBox_specmax.setKeyboardTracking(False)
        self.spinBox_specmax.setMinimum(-200)
        self.spinBox_specmax.setMaximum(200)
        self.spinBox_specmax.setProperty("value", DEFAULT_LEVEL_MAX)
        self.spinBox_specmax.setObjectName("longlevels_specmax")
        self.spinBox_specmax.setSuffix(" dB")

        self.spinBox_resptime = QtWidgets.QSpinBox(self)
        self.spinBox_resptime.setKeyboardTracking(False)
        self.spinBox_resptime.setMinimum(1)
        self.spinBox_resptime.setMaximum(20)
        self.spinBox_resptime.setProperty("value", DEFAULT_RESPONSE_TIME)
        self.spinBox_resptime.setObjectName("longlevels_resptime")
        self.spinBox_resptime.setSuffix(" sec")

        self.spinBox_timemax = QtWidgets.QSpinBox(self)
        self.spinBox_timemax.setKeyboardTracking(False)
        self.spinBox_timemax.setMinimum(5)
        self.spinBox_timemax.setMaximum(3600)
        self.spinBox_timemax.setProperty("value", DEFAULT_MAXTIME)
        self.spinBox_timemax.setObjectName("longlevels_timemax")
        self.spinBox_timemax.setSuffix(" sec")


        self.formLayout.addRow("Max:", self.spinBox_specmax)
        self.formLayout.addRow("Min:", self.spinBox_specmin)
        self.formLayout.addRow("Response Time", self.spinBox_resptime)
        self.formLayout.addRow("Time Range:", self.spinBox_timemax)

        self.setLayout(self.formLayout)

        self.spinBox_specmin.valueChanged.connect(self.parent().setmin)
        self.spinBox_specmax.valueChanged.connect(self.parent().setmax)
        self.spinBox_resptime.valueChanged.connect(self.parent().setresptime)
        self.spinBox_timemax.valueChanged.connect(self.parent().setduration)

    # method
    def saveState(self, settings):
        settings.setValue("Min", self.spinBox_specmin.value())
        settings.setValue("Max", self.spinBox_specmax.value())
        settings.setValue("RespTime", self.spinBox_resptime.value())
        settings.setValue("TimeMax", self.spinBox_timemax.value())

    # method
    def restoreState(self, settings):
        colorMin = settings.value("Min", DEFAULT_LEVEL_MIN, type=int)
        self.spinBox_specmin.setValue(colorMin)
        colorMax = settings.value("Max", DEFAULT_LEVEL_MAX, type=int)
        self.spinBox_specmax.setValue(colorMax)
        resptime = settings.value("RespTime", DEFAULT_RESPONSE_TIME, type=int)
        self.spinBox_resptime.setValue(resptime)
        timemax = settings.value("TimeMax", DEFAULT_MAXTIME, type=int)
        self.spinBox_timemax.setValue(timemax)
