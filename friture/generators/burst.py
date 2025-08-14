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
from friture.audiobackend import SAMPLING_RATE
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal

DEFAULT_BURST_PERIOD_S = 1.

class BurstGenerator:
    name = "Burst"

    def __init__(self, parent):
        self._view_model = Burst_Generator_Settings_View_Model(parent)

    def view_model(self):
        return self._view_model

    def qml_file_name(self) -> str:
        return "BurstSettings.qml"

    def signal(self, t):
        floatdata = np.zeros(t.shape)
        i = (t * SAMPLING_RATE) % (self._view_model.period * SAMPLING_RATE)
        n = 1
        ind_plus = np.where(i < n)
        floatdata[ind_plus] = 1.

        # ind_minus = np.where((i >= n)*(i < 2*n))
        # floatdata[ind_minus] = -1.

        return floatdata


class Burst_Generator_Settings_View_Model(QObject):
    period_changed = pyqtSignal(float)

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self._period = DEFAULT_BURST_PERIOD_S

    @pyqtProperty(float, notify=period_changed)
    def period(self) -> float:
        return self._period

    @period.setter # type: ignore
    def period(self, period: float):
        if self._period != period:
            self._period = period
            self.period_changed.emit(period)

    def saveState(self, settings):
        settings.setValue("burst period", self.period)

    def restoreState(self, settings):
        burst_period = settings.value("burst period", DEFAULT_BURST_PERIOD_S, type=float)
        self.period = burst_period