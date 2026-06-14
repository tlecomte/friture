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

from friture.ballistic_peak import BallisticPeak
from friture.level_data import LevelData

class LevelViewModel(QtCore.QObject):
    two_channels_changed = QtCore.pyqtSignal(bool)
    unit_label_changed = QtCore.pyqtSignal(str)
    weighting_suffix_changed = QtCore.pyqtSignal(str)
    calibrate_requested = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._two_channels = False
        self._unit_label = "dB FS"
        self._weighting_suffix = ""

        self._level_data = LevelData(self)
        self._level_data_2 = LevelData(self)
        self._level_data_slow = LevelData(self)
        self._level_data_slow_2 = LevelData(self)
        self._level_data_ballistic = BallisticPeak(self)
        self._level_data_ballistic_2 = BallisticPeak(self)

    @pyqtProperty(bool, notify=two_channels_changed) # type: ignore
    def two_channels(self):
        return self._two_channels

    @two_channels.setter # type: ignore
    def two_channels(self, two_channels):
        if self._two_channels != two_channels:
            self._two_channels = two_channels
            self.two_channels_changed.emit(two_channels)

    @pyqtProperty(str, notify=unit_label_changed)  # type: ignore
    def unit_label(self) -> str:
        return self._unit_label

    @unit_label.setter  # type: ignore
    def unit_label(self, unit_label: str) -> None:
        if self._unit_label != unit_label:
            self._unit_label = unit_label
            self.unit_label_changed.emit(unit_label)
            self._refresh_meter_iec_display()

    def _refresh_meter_iec_display(self) -> None:
        for level_data in (
            self._level_data,
            self._level_data_2,
            self._level_data_slow,
            self._level_data_slow_2,
        ):
            level_data.level_rms_changed.emit(level_data.level_rms)
            level_data.level_max_changed.emit(level_data.level_max)

    @pyqtProperty(str, notify=weighting_suffix_changed)  # type: ignore
    def weighting_suffix(self) -> str:
        return self._weighting_suffix

    @weighting_suffix.setter  # type: ignore
    def weighting_suffix(self, weighting_suffix: str) -> None:
        if self._weighting_suffix != weighting_suffix:
            self._weighting_suffix = weighting_suffix
            self.weighting_suffix_changed.emit(weighting_suffix)

    @pyqtProperty(LevelData, constant = True) # type: ignore
    def level_data(self):
        return self._level_data

    @pyqtProperty(LevelData, constant = True) # type: ignore
    def level_data_2(self):
        return self._level_data_2

    @pyqtProperty(LevelData, constant = True) # type: ignore
    def level_data_slow(self):
        return self._level_data_slow

    @pyqtProperty(LevelData, constant = True) # type: ignore
    def level_data_slow_2(self):
        return self._level_data_slow_2

    @pyqtProperty(LevelData, constant = True) # type: ignore
    def level_data_ballistic(self):
        return self._level_data_ballistic

    @pyqtProperty(LevelData, constant = True) # type: ignore
    def level_data_ballistic_2(self):
        return self._level_data_ballistic_2