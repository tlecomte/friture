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
from PyQt5.QtCore import pyqtProperty # type: ignore

PEAK_DECAY_RATE = (1.0 - 3E-6/500.)
# Number of cycles the peak stays on hold before fall-off.
PEAK_FALLOFF = 32

class BallisticPeak(QtCore.QObject):
    peak_changed = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._peak_iec = 0
        self._peak_hold_counter = 0
        self._peak_decay_factor = PEAK_DECAY_RATE

    @pyqtProperty(float, notify=peak_changed)
    def peak_iec(self):
        return self._peak_iec

    @peak_iec.setter # type: ignore
    def peak_iec(self, peak_iec):

        # peak-hold-then-decay mechanism
        if peak_iec > self._peak_iec:
            # follow the peak
            new_peak_iec = peak_iec
            self._peak_hold_counter = 0  # reset the hold
            self._peak_decay_factor = PEAK_DECAY_RATE
        elif self._peak_hold_counter + 1 <= PEAK_FALLOFF:
            # hold
            new_peak_iec = self._peak_iec
            self._peak_hold_counter += 1
        else:
            # decay
            new_peak_iec = self._peak_decay_factor * float(self._peak_iec)
            if new_peak_iec < peak_iec:
                new_peak_iec = peak_iec
                self._peak_hold_counter = 0  # reset the hold
                self._peak_decay_factor = PEAK_DECAY_RATE
            else:
                self._peak_decay_factor *= self._peak_decay_factor

        if self._peak_iec != new_peak_iec:
            self._peak_iec = new_peak_iec
            self.peak_changed.emit(new_peak_iec)
