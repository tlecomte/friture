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
from PyQt5.QtQml import QQmlListProperty

from friture.axis import Axis
from friture.curve import Curve

class Scope_Data(QtCore.QObject):
    two_channels_changed = QtCore.pyqtSignal(bool)
    plot_items_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._two_channels = False
        self._plot_items = []
        self._horizontal_axis = Axis()
        self._vertical_axis = Axis()

    @pyqtProperty(QQmlListProperty, notify=plot_items_changed)
    def plot_items(self):
        return QQmlListProperty(Curve, self, self._plot_items)
    
    def add_plot_item(self, plot_item):
        self._plot_items.append(plot_item)
        self.plot_items_changed.emit()

    def remove_plot_item(self, plot_item):
        self._plot_items.remove(plot_item)
        self.plot_items_changed.emit()

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