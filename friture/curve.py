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
from PyQt5.QtGui import QPolygonF

class Curve(QtCore.QObject):
    data_polygon_changed = QtCore.pyqtSignal(QPolygonF)
    name_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._data_polygon = QPolygonF()
        self._name = ""
    
    @pyqtProperty(QPolygonF, notify=data_polygon_changed)
    def data_polygon(self):
        return self._data_polygon
    
    @data_polygon.setter
    def data_polygon(self, p):
        if self._data_polygon != p:
            self._data_polygon = p
            self.data_polygon_changed.emit(p)
    
    @pyqtProperty(str, notify=name_changed)
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        if self._name != name:
            self._name = name
            self.name_changed.emit(name)