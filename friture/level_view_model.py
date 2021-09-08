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

    def __init__(self, parent=None):
        super().__init__(parent)

        self._two_channels = False

        self._level_data = LevelData(self)
        self._level_data_2 = LevelData(self)
        self._level_data_slow = LevelData(self)
        self._level_data_slow_2 = LevelData(self)
        self._level_data_ballistic = BallisticPeak(self)
        self._level_data_ballistic_2 = BallisticPeak(self)

    @pyqtProperty(bool, notify=two_channels_changed)
    def two_channels(self):
        return self._two_channels
    
    @two_channels.setter
    def two_channels(self, two_channels):
        if self._two_channels != two_channels:
            self._two_channels = two_channels
            self.two_channels_changed.emit(two_channels)

    @pyqtProperty(LevelData, constant = True)
    def level_data(self):
        return self._level_data
    
    @pyqtProperty(LevelData, constant = True)
    def level_data_2(self):
        return self._level_data_2
    
    @pyqtProperty(LevelData, constant = True)
    def level_data_slow(self):
        return self._level_data_slow
    
    @pyqtProperty(LevelData, constant = True)
    def level_data_slow_2(self):
        return self._level_data_slow_2
    
    @pyqtProperty(LevelData, constant = True)
    def level_data_ballistic(self):
        return self._level_data_ballistic
    
    @pyqtProperty(LevelData, constant = True)
    def level_data_ballistic_2(self):
        return self._level_data_ballistic_2