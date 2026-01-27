#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 Timothée Lecomte

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
from PyQt5.QtCore import pyqtProperty, pyqtSlot

from friture.scope_data import Scope_Data

class Spectrogram_Data(Scope_Data):
    target_frequencies_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._target_frequencies = []


    @pyqtProperty('QVariantList', notify=target_frequencies_changed) # type: ignore
    def target_frequencies(self):
        return self._target_frequencies

    @target_frequencies.setter
    def target_frequencies(self, freqs):
        if self._target_frequencies != freqs:
            self._target_frequencies = freqs
            self.target_frequencies_changed.emit()

    @pyqtSlot(float)
    def add_target_frequency(self, frequency):
        if frequency not in self._target_frequencies:
            self._target_frequencies.append(frequency)
            self.target_frequencies_changed.emit()

    @pyqtSlot(float)
    def remove_target_frequency(self, frequency):
        self.target_frequencies = [f for f in self._target_frequencies if f != frequency]
