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
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal

DEFAULT_SINE_FREQUENCY = 440.

class SineGenerator:

    name = "Sine"

    def __init__(self, parent):
        self._view_model = Sine_Generator_Settings_View_Model(parent)

    def view_model(self):
        return self._view_model

    def qml_file_name(self) -> str:
        return "SineSettings.qml"

    def signal(self, t):
        self._view_model.lastt = t[-1]
        return np.sin(2. * np.pi * t * self._view_model.frequency + self._view_model.offset)

class Sine_Generator_Settings_View_Model(QObject):
    frequency_changed = pyqtSignal(float)

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self._frequency = DEFAULT_SINE_FREQUENCY
        self.offset = 0
        self.lastt = 0

    @pyqtProperty(float, notify=frequency_changed)
    def frequency(self) -> float:
        return self._frequency

    @frequency.setter # type: ignore
    def frequency(self, frequency: float):
        if self._frequency != frequency:
            oldf = self._frequency
            self._frequency = frequency

            # the offset is adapted to avoid phase break
            lastphase = 2. * np.pi * self.lastt * oldf + self.offset
            newphase = 2. * np.pi * self.lastt * self._frequency+ self.offset
            self.offset += (lastphase - newphase)
            self.offset %= 2. * np.pi

            self.frequency_changed.emit(frequency)

    def saveState(self, settings):
        settings.setValue("sine frequency", self.frequency)

    def restoreState(self, settings):
        frequency = settings.value("sine frequency", DEFAULT_SINE_FREQUENCY, type=float)
        self.frequency = frequency
