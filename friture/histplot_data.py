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
from PyQt5.QtQml import QQmlListProperty

from friture.bar_label import BarLabel
from friture.scope_data import Scope_Data

class HistPlot_Data(Scope_Data):
    bar_labels_changed = QtCore.pyqtSignal()
    bar_labels_x_distance_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._bar_labels = []
        self._bar_labels_x_distance = 0.
    
    def setBarLabels(self, x, unscaled_x, y):
        x_distance = x[1] - x[0]
        if self._bar_labels_x_distance != x_distance:
            self._bar_labels_x_distance = x_distance
            self.bar_labels_x_distance_changed.emit()

        label_count = x.shape[0]
        
        # never display more than 60 labels
        # it is not useful visually
        # and the loop to build them would be too slow
        if label_count > 60:
            label_count = 0

        if label_count != len(self._bar_labels):
            self._bar_labels = [BarLabel(self) for i in range(label_count)]
            self.bar_labels_changed.emit()

        for i in range(label_count):
            self._bar_labels[i].setData(x[i], unscaled_x[i], y[i])

    @pyqtProperty(QQmlListProperty, notify=bar_labels_changed)
    def barLabels(self):
        return QQmlListProperty(BarLabel, self, self._bar_labels)

    @pyqtProperty(float, notify=bar_labels_x_distance_changed)
    def bar_labels_x_distance(self):
        return self._bar_labels_x_distance
