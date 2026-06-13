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

from friture.iec import level_db_to_meter_fraction, meter_level_for_bar

class LevelData(QtCore.QObject):
    level_rms_changed = QtCore.pyqtSignal(float)
    level_max_changed = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._level_rms = -30.
        self._level_max = -30.
        self._level_rms_raw = -30.
        self._level_max_raw = -30.

    @pyqtProperty(float, notify=level_rms_changed) # type: ignore
    def level_rms(self):
        return self._level_rms

    @pyqtProperty(float, notify=level_rms_changed) # type: ignore
    def level_rms_iec(self):
        unit_label = self._meter_unit_label()
        meter_db = meter_level_for_bar(
            self._level_rms, self._level_rms_raw, unit_label
        )
        return level_db_to_meter_fraction(meter_db, unit_label)

    @level_rms.setter # type: ignore
    def level_rms(self, level_rms):
        if self._level_rms != level_rms:
            self._level_rms = level_rms
            self.level_rms_changed.emit(level_rms)

    @pyqtProperty(float, notify=level_max_changed) # type: ignore
    def level_max(self):
        return self._level_max

    @pyqtProperty(float, notify=level_max_changed) # type: ignore
    def level_max_iec(self):
        unit_label = self._meter_unit_label()
        meter_db = meter_level_for_bar(
            self._level_max, self._level_max_raw, unit_label
        )
        return level_db_to_meter_fraction(meter_db, unit_label)

    @level_max.setter # type: ignore
    def level_max(self, level_max):
        if self._level_max != level_max:
            self._level_max = level_max
            self.level_max_changed.emit(level_max)

    @property
    def level_rms_raw(self) -> float:
        return self._level_rms_raw

    @level_rms_raw.setter
    def level_rms_raw(self, level_rms_raw: float) -> None:
        self._level_rms_raw = level_rms_raw

    @property
    def level_max_raw(self) -> float:
        return self._level_max_raw

    @level_max_raw.setter
    def level_max_raw(self, level_max_raw: float) -> None:
        self._level_max_raw = level_max_raw

    def _meter_unit_label(self) -> str:
        parent = self.parent()
        unit_label = getattr(parent, "unit_label", None)
        if unit_label:
            return unit_label
        return "dB FS"