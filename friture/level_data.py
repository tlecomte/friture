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

from friture.iec import dB_to_IEC

class LevelData(QtCore.QObject):
    level_rms_changed = QtCore.pyqtSignal(float)
    level_max_changed = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._level_rms = -30.
        self._level_max = -30.

    @pyqtProperty(float, notify=level_rms_changed)
    def level_rms(self):
        return self._level_rms
    
    @pyqtProperty(float, notify=level_rms_changed)
    def level_rms_iec(self):
        return dB_to_IEC(self._level_rms)
    
    @level_rms.setter
    def level_rms(self, level_rms):
        if self._level_rms != level_rms:
            self._level_rms = level_rms
            self.level_rms_changed.emit(level_rms)

    @pyqtProperty(float, notify=level_max_changed)
    def level_max(self):
        return self._level_max

    @pyqtProperty(float, notify=level_max_changed)
    def level_max_iec(self):
        return dB_to_IEC(self._level_max)
    
    @level_max.setter
    def level_max(self, level_max):
        if self._level_max != level_max:
            self._level_max = level_max
            self.level_max_changed.emit(level_max)