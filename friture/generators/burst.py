#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

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

import numpy as np
from PyQt5 import QtWidgets
from friture.audiobackend import SAMPLING_RATE

DEFAULT_BURST_PERIOD_S = 1.


class BurstGenerator:
    name = "Burst"

    def __init__(self, parent):
        self.T = 1.

        self.settings = SettingsWidget(parent)
        self.settings.spinBox_burst_period.valueChanged.connect(self.setT)

    def setT(self, T):
        self.T = T

    def settingsWidget(self):
        return self.settings

    def signal(self, t):
        floatdata = np.zeros(t.shape)
        i = (t * SAMPLING_RATE) % (self.T * SAMPLING_RATE)
        n = 1
        ind_plus = np.where(i < n)
        floatdata[ind_plus] = 1.

        # ind_minus = np.where((i >= n)*(i < 2*n))
        # floatdata[ind_minus] = -1.

        return floatdata


class SettingsWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.spinBox_burst_period = QtWidgets.QDoubleSpinBox(self)
        self.spinBox_burst_period.setKeyboardTracking(False)
        self.spinBox_burst_period.setDecimals(2)
        self.spinBox_burst_period.setSingleStep(1)
        self.spinBox_burst_period.setMinimum(0.01)
        self.spinBox_burst_period.setMaximum(60)
        self.spinBox_burst_period.setProperty("value", DEFAULT_BURST_PERIOD_S)
        self.spinBox_burst_period.setObjectName("spinBox_burst_period")
        self.spinBox_burst_period.setSuffix(" s")

        self.formLayout = QtWidgets.QFormLayout(self)

        self.formLayout.addRow("Period:", self.spinBox_burst_period)

        self.setLayout(self.formLayout)

    def saveState(self, settings):
        settings.setValue("burst period", self.spinBox_burst_period.value())

    def restoreState(self, settings):
        burst_period = settings.value("burst period", DEFAULT_BURST_PERIOD_S, type=float)
        self.spinBox_burst_period.setValue(burst_period)
