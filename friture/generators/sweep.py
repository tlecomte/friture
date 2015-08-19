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

DEFAULT_SWEEP_STARTFREQUENCY = 20.
DEFAULT_SWEEP_STOPFREQUENCY = 22000.
DEFAULT_SWEEP_PERIOD_S = 1.

class SweepGenerator:
    def __init__(self, parent, logger):
        self.f1 = 20.
        self.f2 = 22000.
        self.T = 1.
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)

        self.settings = SettingsWidget(parent, logger)
        self.settings.spinBox_sweep_startfrequency.valueChanged.connect(self.setf1)
        self.settings.spinBox_sweep_stopfrequency.valueChanged.connect(self.setf2)
        self.settings.spinBox_sweep_period.valueChanged.connect(self.setT)

    def settingsWidget(self):
        return self.settings

    def computeKL(self, f1, f2, T):
        w1 = 2*np.pi*f1
        w2 = 2*np.pi*f2
        K = w1*T/np.log(w2/w1)
        L = T/np.log(w2/w1)
        return L, K

    def setf1(self, f1):
        self.f1 = f1
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)

    def setf2(self, f2):
        self.f2 = f2
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)

    def setT(self, T):
        self.T = T
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)

    def signal(self, t):
        # https://ccrma.stanford.edu/realsimple/imp_meas/Sine_Sweep_Measurement_Theory.html

        #f = (self.f2 - self.f1)*(1. + np.sin(2*np.pi*t/self.T))/2. + self.f1
        #return np.sin(2*np.pi*t*f)
        return np.sin(self.K*(np.exp(t%self.T/self.L) - 1.))

class SettingsWidget(QtWidgets.QWidget):
    def __init__(self, parent, logger):
        super().__init__(parent)

        self.logger = logger

        self.spinBox_sweep_startfrequency = QtWidgets.QSpinBox(self)
        self.spinBox_sweep_startfrequency.setKeyboardTracking(False)
        self.spinBox_sweep_startfrequency.setMinimum(20)
        self.spinBox_sweep_startfrequency.setMaximum(22000)
        self.spinBox_sweep_startfrequency.setProperty("value", DEFAULT_SWEEP_STARTFREQUENCY)
        self.spinBox_sweep_startfrequency.setObjectName("spinBox_sweep_startfrequency")
        self.spinBox_sweep_startfrequency.setSuffix(" Hz")

        self.spinBox_sweep_stopfrequency = QtWidgets.QSpinBox(self)
        self.spinBox_sweep_stopfrequency.setKeyboardTracking(False)
        self.spinBox_sweep_stopfrequency.setMinimum(20)
        self.spinBox_sweep_stopfrequency.setMaximum(22000)
        self.spinBox_sweep_stopfrequency.setProperty("value", DEFAULT_SWEEP_STOPFREQUENCY)
        self.spinBox_sweep_stopfrequency.setObjectName("spinBox_sweep_stopfrequency")
        self.spinBox_sweep_stopfrequency.setSuffix(" Hz")

        self.spinBox_sweep_period = QtWidgets.QDoubleSpinBox(self)
        self.spinBox_sweep_period.setKeyboardTracking(False)
        self.spinBox_sweep_period.setDecimals(2)
        self.spinBox_sweep_period.setSingleStep(1)
        self.spinBox_sweep_period.setMinimum(0.01)
        self.spinBox_sweep_period.setMaximum(60)
        self.spinBox_sweep_period.setProperty("value", DEFAULT_SWEEP_PERIOD_S)
        self.spinBox_sweep_period.setObjectName("spinBox_sweep_period")
        self.spinBox_sweep_period.setSuffix(" s")

        self.formLayout = QtWidgets.QFormLayout(self)

        self.formLayout.addRow("Start frequency:", self.spinBox_sweep_startfrequency)
        self.formLayout.addRow("Stop frequency:", self.spinBox_sweep_stopfrequency)
        self.formLayout.addRow("Period:", self.spinBox_sweep_period)

        self.setLayout(self.formLayout)

    def saveState(self, settings):
        settings.setValue("sweep start frequency", self.spinBox_sweep_startfrequency.value())
        settings.setValue("sweep stop frequency", self.spinBox_sweep_stopfrequency.value())
        settings.setValue("sweep period", self.spinBox_sweep_period.value())

    def restoreState(self, settings):
        sweep_start_frequency = float(settings.value("sweep start frequency", DEFAULT_SWEEP_STARTFREQUENCY))
        self.spinBox_sweep_startfrequency.setValue(sweep_start_frequency)
        sweep_stop_frequency = float(settings.value("sweep stop frequency", DEFAULT_SWEEP_STOPFREQUENCY))
        self.spinBox_sweep_stopfrequency.setValue(sweep_stop_frequency)
        sweep_period = float(settings.value("sweep period", DEFAULT_SWEEP_PERIOD_S))
        self.spinBox_sweep_period.setValue(sweep_period)
