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
from PyQt5.QtQml import QQmlListProperty # type: ignore

from friture.axis import Axis
from friture.curve import Curve

class Scope_Data(QtCore.QObject):
    show_color_axis_changed = QtCore.pyqtSignal(bool)
    show_legend_changed = QtCore.pyqtSignal(bool)
    plot_items_changed = QtCore.pyqtSignal()
    reference_overlay_changed = QtCore.pyqtSignal()
    reference_overlay_visible_changed = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._plot_items = []
        self._reference_overlay = Curve(self)
        self._reference_overlay_visible = False
        self._horizontal_axis = Axis(self)
        self._vertical_axis = Axis(self)
        self._color_axis = Axis(self)
        self._show_color_axis = False
        self._show_legend = True

    @pyqtProperty(QQmlListProperty, notify=plot_items_changed) # type: ignore
    def plot_items(self):
        return QQmlListProperty(Curve, self, self._plot_items)

    def insert_plot_item(self, index, plot_item):
        self._plot_items.insert(index, plot_item)
        self.plot_items_changed.emit()

    def add_plot_item(self, plot_item):
        self._plot_items.append(plot_item)
        plot_item.setParent(self) # take ownership
        self.plot_items_changed.emit()

    def remove_plot_item(self, plot_item):
        self._plot_items.remove(plot_item)
        self.plot_items_changed.emit()

    @pyqtProperty(Axis, constant=True) # type: ignore
    def horizontal_axis(self):
        return self._horizontal_axis

    @pyqtProperty(Axis, constant=True) # type: ignore
    def vertical_axis(self):
        return self._vertical_axis

    @pyqtProperty(Axis, constant=True)
    def color_axis(self):
        return self._color_axis
    
    @pyqtProperty(bool, notify=show_color_axis_changed)
    def show_color_axis(self):
        return self._show_color_axis
    
    @show_color_axis.setter
    def show_color_axis(self, show_color_axis):
        if self._show_color_axis != show_color_axis:
            self._show_color_axis = show_color_axis
            self.show_color_axis_changed.emit(show_color_axis)
    
    @pyqtProperty(bool, notify=show_legend_changed) # type: ignore
    def show_legend(self):
        return self._show_legend

    @show_legend.setter # type: ignore
    def show_legend(self, show_legend):
        if self._show_legend != show_legend:
            self._show_legend = show_legend
            self.show_legend_changed.emit(show_legend)

    @pyqtProperty(Curve, notify=reference_overlay_changed)  # type: ignore
    def reference_overlay(self):
        return self._reference_overlay

    def set_reference_overlay(self, curve: Curve) -> None:
        if self._reference_overlay is not curve:
            self._reference_overlay = curve
            self.reference_overlay_changed.emit()

    @pyqtProperty(bool, notify=reference_overlay_visible_changed)  # type: ignore
    def reference_overlay_visible(self):
        return self._reference_overlay_visible

    def set_reference_overlay_visible(self, visible: bool) -> None:
        if self._reference_overlay_visible != visible:
            self._reference_overlay_visible = visible
            self.reference_overlay_visible_changed.emit(visible)
