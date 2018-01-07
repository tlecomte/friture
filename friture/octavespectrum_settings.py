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

import logging

from PyQt5 import QtWidgets

# shared with octavespectrum.py
DEFAULT_SPEC_MIN = -80
DEFAULT_SPEC_MAX = -20
DEFAULT_WEIGHTING = 0  # None
DEFAULT_BANDSPEROCTAVE = 3
DEFAULT_BANDSPEROCTAVE_INDEX = 1
DEFAULT_RESPONSE_TIME = 1.
DEFAULT_RESPONSE_TIME_INDEX = 3


class OctaveSpectrum_Settings_Dialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)

        self.setWindowTitle("Octave Spectrum settings")

        self.formLayout = QtWidgets.QFormLayout(self)

        self.comboBox_bandsperoctave = QtWidgets.QComboBox(self)
        self.comboBox_bandsperoctave.setObjectName("comboBox_bandsperoctave")
        self.comboBox_bandsperoctave.addItem("1")
        self.comboBox_bandsperoctave.addItem("3")
        self.comboBox_bandsperoctave.addItem("6")
        self.comboBox_bandsperoctave.addItem("12")
        self.comboBox_bandsperoctave.addItem("24")
        self.comboBox_bandsperoctave.setCurrentIndex(DEFAULT_BANDSPEROCTAVE_INDEX)

        self.spinBox_specmin = QtWidgets.QSpinBox(self)
        self.spinBox_specmin.setKeyboardTracking(False)
        self.spinBox_specmin.setMinimum(-200)
        self.spinBox_specmin.setMaximum(200)
        self.spinBox_specmin.setProperty("value", DEFAULT_SPEC_MIN)
        self.spinBox_specmin.setObjectName("spinBox_specmin")
        self.spinBox_specmin.setSuffix(" dB")

        self.spinBox_specmax = QtWidgets.QSpinBox(self)
        self.spinBox_specmax.setKeyboardTracking(False)
        self.spinBox_specmax.setMinimum(-200)
        self.spinBox_specmax.setMaximum(200)
        self.spinBox_specmax.setProperty("value", DEFAULT_SPEC_MAX)
        self.spinBox_specmax.setObjectName("spinBox_specmax")
        self.spinBox_specmax.setSuffix(" dB")

        self.comboBox_weighting = QtWidgets.QComboBox(self)
        self.comboBox_weighting.setObjectName("weighting")
        self.comboBox_weighting.addItem("None")
        self.comboBox_weighting.addItem("A")
        self.comboBox_weighting.addItem("B")
        self.comboBox_weighting.addItem("C")
        self.comboBox_weighting.setCurrentIndex(DEFAULT_WEIGHTING)

        self.comboBox_response_time = QtWidgets.QComboBox(self)
        self.comboBox_response_time.setObjectName("response_time")
        self.comboBox_response_time.addItem("25 ms (Impulse)")
        self.comboBox_response_time.addItem("125 ms (Fast)")
        self.comboBox_response_time.addItem("300 ms")
        self.comboBox_response_time.addItem("1s (Slow)")
        self.comboBox_response_time.setCurrentIndex(DEFAULT_RESPONSE_TIME_INDEX)

        self.formLayout.addRow("Bands per octave:", self.comboBox_bandsperoctave)
        self.formLayout.addRow("Min:", self.spinBox_specmin)
        self.formLayout.addRow("Max:", self.spinBox_specmax)
        self.formLayout.addRow("Middle-ear weighting:", self.comboBox_weighting)
        self.formLayout.addRow("Response time:", self.comboBox_response_time)

        self.setLayout(self.formLayout)

        self.comboBox_bandsperoctave.currentIndexChanged.connect(self.bandsperoctavechanged)
        self.spinBox_specmin.valueChanged.connect(self.parent().setmin)
        self.spinBox_specmax.valueChanged.connect(self.parent().setmax)
        self.comboBox_weighting.currentIndexChanged.connect(self.parent().setweighting)
        self.comboBox_response_time.currentIndexChanged.connect(self.responsetimechanged)

    # slot
    def bandsperoctavechanged(self, index):
        bandsperoctave = 3 * 2 ** (index - 1) if index >= 1 else 1
        self.logger.info("bandsperoctavechanged slot %d %d", index, bandsperoctave)
        self.parent().setbandsperoctave(bandsperoctave)

    # slot
    def responsetimechanged(self, index):
        if index == 0:
            response_time = 0.025
        elif index == 1:
            response_time = 0.125
        elif index == 2:
            response_time = 0.3
        elif index == 3:
            response_time = 1.
        self.logger.info("responsetimechanged slot %d %d", index, response_time)
        self.parent().setresponsetime(response_time)

    # method
    def saveState(self, settings):
        settings.setValue("bandsPerOctave", self.comboBox_bandsperoctave.currentIndex())
        settings.setValue("Min", self.spinBox_specmin.value())
        settings.setValue("Max", self.spinBox_specmax.value())
        settings.setValue("weighting", self.comboBox_weighting.currentIndex())
        settings.setValue("response_time", self.comboBox_response_time.currentIndex())

    # method
    def restoreState(self, settings):
        bandsPerOctave = settings.value("bandsPerOctave", DEFAULT_BANDSPEROCTAVE_INDEX, type=int)
        self.comboBox_bandsperoctave.setCurrentIndex(bandsPerOctave)
        colorMin = settings.value("Min", DEFAULT_SPEC_MIN, type=int)
        self.spinBox_specmin.setValue(colorMin)
        colorMax = settings.value("Max", DEFAULT_SPEC_MAX, type=int)
        self.spinBox_specmax.setValue(colorMax)
        weighting = settings.value("weighting", DEFAULT_WEIGHTING, type=int)
        self.comboBox_weighting.setCurrentIndex(weighting)
        response_time_index = settings.value("response_time", DEFAULT_RESPONSE_TIME_INDEX, type=int)
        self.comboBox_response_time.setCurrentIndex(response_time_index)
