#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 Timothée Lecomte

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

class BarLabel(QtCore.QObject):
    x_changed = QtCore.pyqtSignal()
    y_changed = QtCore.pyqtSignal()
    unscaled_x_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._x = 0.
        self._y = 0.
        self._unscaled_x = ""

    def setData(self, x, unscaled_x, y):
        if self._x != x:
            self._x = x
            self.x_changed.emit()

        if self._unscaled_x != unscaled_x:
            self._unscaled_x = unscaled_x
            self.unscaled_x_changed.emit()

        if self._y != y:
            self._y = y
            self.y_changed.emit()

    @pyqtProperty(float, notify=x_changed)
    def x(self):
        return self._x

    @pyqtProperty(float, notify=y_changed)
    def y(self):
        return self._y

    @pyqtProperty(str, notify=unscaled_x_changed)
    def unscaled_x(self):
        return self._unscaled_x
