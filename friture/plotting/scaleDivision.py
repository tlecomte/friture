#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Timothée Lecomte

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
from PyQt5.QtQml import QQmlListProperty # type: ignore

import friture.plotting.frequency_scales as fscales
from friture.plotting.coordinateTransform import CoordinateTransform

class Tick(QtCore.QObject):
    def __init__(self, value, logical_value, parent=None):
        super().__init__(parent)
        self._value = value
        self._logical_value = logical_value

    @pyqtProperty(str, constant = True) # type: ignore
    def value(self):
        return self._value

    @pyqtProperty(float, constant = True) # type: ignore
    def logicalValue(self):
        return self._logical_value

# takes min/max of the scale, and returns appropriate ticks (selected for proper number, rounding)
class ScaleDivision(QtCore.QObject):
    logical_major_ticks_changed = QtCore.pyqtSignal()
    logical_minor_ticks_changed = QtCore.pyqtSignal()

    def __init__(self, scale_min, scale_max, parent=None):
        super().__init__(parent)

        self.scale_min = scale_min
        self.scale_max = scale_max
        self.scale = fscales.Linear
        self._logical_coordinate_transform = CoordinateTransform(scale_min, scale_max, 1., 0., 0.)
        self._update_ticks()

    def setRange(self, scale_min, scale_max):
        self.scale_min = scale_min
        self.scale_max = scale_max
        self._logical_coordinate_transform.setRange(scale_min, scale_max)
        self._update_ticks()

    def setScale(self, scale):
        self.scale = scale
        self._logical_coordinate_transform.setScale(scale)
        self._update_ticks()

    def majorTicks(self):
        return self.major_ticks

    def minorTicks(self):
        return self.minor_ticks

    @pyqtProperty(QQmlListProperty, notify=logical_major_ticks_changed) # type: ignore
    def logicalMajorTicks(self):
        return QQmlListProperty(Tick, self, self._logical_major_ticks)

    @pyqtProperty(QQmlListProperty, notify=logical_minor_ticks_changed) # type: ignore
    def logicalMinorTicks(self):
        return QQmlListProperty(Tick, self, self._logical_minor_ticks)

    def _update_ticks(self):
        self.major_ticks, self.minor_ticks = self.scale.ticks(self.scale_min, self.scale_max)

        if len(self.major_ticks) < 2:
            interval = 0
        else:
            interval = self.major_ticks[1] - self.major_ticks[0]
        precision = fscales.numberPrecision(interval)
        digits = max(0, int(-precision))

        def buildTick(tick):
            value = '{0:.{1}f}'.format(tick, digits)
            logical_value = self._logical_coordinate_transform.toScreen(tick)
            return Tick(value, logical_value)

        self._logical_major_ticks = list(map(buildTick, self.major_ticks))
        self.logical_major_ticks_changed.emit()

        def buildTick(tick):
            value = tick
            logical_value = self._logical_coordinate_transform.toScreen(tick)
            return Tick(value, logical_value)

        self._logical_minor_ticks = list(map(buildTick, self.minor_ticks))
        self.logical_minor_ticks_changed.emit()
