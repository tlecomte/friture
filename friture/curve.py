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
import numpy

class Curve(QtCore.QObject):
    data_changed = QtCore.pyqtSignal()
    name_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._name = ""
        self._x_array = numpy.array([0])
        self._y_array = numpy.array([0])

    def setData(self, x_array, y_array):
        self._x_array = x_array
        self._y_array = y_array
        self.data_changed.emit()
    
    def x_array(self):
        return self._x_array

    def y_array(self):
        return self._y_array
    
    @pyqtProperty(str, notify=name_changed)
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        if self._name != name:
            self._name = name
            self.name_changed.emit(name)