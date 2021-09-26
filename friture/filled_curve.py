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

from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtProperty
import numpy

class CurveType(Enum):
    SIGNAL = 1
    PEEK = 2

class FilledCurve(QtCore.QObject):
    data_changed = QtCore.pyqtSignal()
    name_changed = QtCore.pyqtSignal(str)

    def __init__(self, curve_type, parent=None):
        super().__init__(parent)

        self._name = ""
        self._curve_type = curve_type
        self._x_left_array = numpy.array([0])
        self._x_right_array = numpy.array([0])
        self._y_array = numpy.array([0])
        self._z_array = numpy.array([0])
        self._baseline = 1. # bottom

    def setData(self, x_left_array, x_right_array, y_array, z_array, baseline):
        self._x_left_array = x_left_array
        self._x_right_array = x_right_array
        self._y_array = y_array
        self._z_array = z_array
        self._baseline = baseline
        self.data_changed.emit()
    
    def x_left_array(self):
        return self._x_left_array

    def x_right_array(self):
        return self._x_right_array

    def y_array(self):
        return self._y_array

    def z_array(self):
        return self._z_array

    def baseline(self):
        return self._baseline
    
    @pyqtProperty(str, notify=name_changed)
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        if self._name != name:
            self._name = name
            self.name_changed.emit(name)
    
    @pyqtProperty(CurveType, constant = True)
    def curve_type(self):
        return self._curve_type
