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

from friture.axis import Axis
from friture.curve import Curve

class Scope_Data(QtCore.QObject):
    two_channels_changed = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._two_channels = False
        self._curve = Curve()
        self._curve_2 = Curve()
        self._horizontal_axis = Axis()
        self._vertical_axis = Axis()

    @pyqtProperty(Curve, constant = True)
    def curve(self):
        return self._curve
    
    @pyqtProperty(Curve, constant = True)
    def curve_2(self):
        return self._curve_2

    @pyqtProperty(bool, notify=two_channels_changed)
    def two_channels(self):
        return self._two_channels
    
    @two_channels.setter
    def two_channels(self, two_channels):
        if self._two_channels != two_channels:
            self._two_channels = two_channels
            self.two_channels_changed.emit(two_channels)

    @pyqtProperty(Axis, constant=True)
    def horizontal_axis(self):
        return self._horizontal_axis

    @pyqtProperty(Axis, constant=True)
    def vertical_axis(self):
        return self._vertical_axis