#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

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
import numpy as np

from friture.scope_data import Scope_Data

def frequency_to_note(freq: float) -> str:
    if np.isnan(freq) or freq <= 0:
        return ""
    # number of semitones from C4
    # A4 = 440Hz and is 9 semitones above C4
    semitone = round(np.log2(freq/440) * 12) + 9
    octave = int(np.floor(semitone / 12)) + 4
    notes = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"]
    return f'{notes[semitone % 12]}{octave}'

def format_frequency(freq: float) -> str:
    if freq < 1000:
        return f'{freq:.0f} Hz ({frequency_to_note(freq)})'
    else:
        return f'{freq/1000:.1f} kHz ({frequency_to_note(freq)})'

class PitchTracker_Data(Scope_Data):

    pitch_changed = QtCore.pyqtSignal(float)

    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)
        self._pitch = 0.0

    @pyqtProperty(str, notify=pitch_changed)
    def pitch(self) -> str:
        if not self._pitch or np.isnan(self._pitch):
            return '--'
        elif self._pitch < 1000:
            return f"{self._pitch:.0f}"
        else:
            return f"{self._pitch/1000:.2f}"

    @pitch.setter # type: ignore
    def pitch(self, pitch: float):
        self._pitch = pitch
        self.pitch_changed.emit(pitch)

    @pyqtProperty(str, notify=pitch_changed) # type: ignore
    def pitch_unit(self) -> str:
        if self._pitch >= 1000.0:
            return "kHz"
        else:
            return "Hz"

    @pyqtProperty(str, notify=pitch_changed) # type: ignore
    def note(self) -> str:
        if not self._pitch or np.isnan(self._pitch):
            return '--'
        else:
            return frequency_to_note(self._pitch)
