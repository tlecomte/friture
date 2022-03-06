#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2021 Timothée Lecomte

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

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtProperty

from friture.scope_data import Scope_Data

class Spectrum_Data(Scope_Data):
    fmax_changed = QtCore.pyqtSignal()
    show_frequency_tracker_changed = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._fmax_value = ""
        self._fmax_logical_value = 0
        self._show_frequency_tracker = True
    
    @pyqtProperty(str, notify=fmax_changed)
    def fmaxValue(self):
        return self._fmax_value

    @pyqtProperty(float, notify=fmax_changed)
    def fmaxLogicalValue(self):
        return self._fmax_logical_value
    
    def setFmax(self, value, logical_value):
        if self._fmax_value != value or self._fmax_logical_value != logical_value:
            self._fmax_value = value
            self._fmax_logical_value = logical_value
            self.fmax_changed.emit()
    
    @pyqtProperty(bool, notify=show_frequency_tracker_changed)
    def showFrequencyTracker(self):
        return self._show_frequency_tracker

    @showFrequencyTracker.setter
    def showFrequencyTracker(self, show_frequency_tracker):
        if self._show_frequency_tracker != show_frequency_tracker:
            self._show_frequency_tracker = show_frequency_tracker
            self.show_frequency_tracker_changed.emit(show_frequency_tracker)
