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

import numpy as np

from PyQt5.QtCore import pyqtSignal, pyqtProperty # type: ignore
from PyQt5.QtQuick import QQuickItem, QSGGeometryNode, QSGGeometry, QSGNode, QSGVertexColorMaterial # type: ignore

from friture.filled_curve import CurveType, FilledCurve

class PlotFilledCurve(QQuickItem):
    curveChanged = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setFlag(QQuickItem.ItemHasContents, True)

        self._curve = FilledCurve(CurveType.SIGNAL)

    @pyqtProperty(FilledCurve, notify=curveChanged)
    def curve(self):
        return self._curve

    @curve.setter # type: ignore
    def curve(self, curve):
        if curve != self._curve:
            self._curve = curve
            if self._curve is not None:
                self._curve.data_changed.connect(self.update)

            self.update()
            self.curveChanged.emit()

    def updatePaintNode(self, paint_node, update_data):

        # clip to the plot area
        # find the first quad that enters the plot area
        enter_indices = np.argwhere((self.curve.x_left_array() < 0.) * (self.curve.x_right_array() > 0.))
        enter_index = enter_indices[0][0] if len(enter_indices) > 0 else 0

        # find the first quad that exits the plot area
        exit_indices = np.argwhere((self.curve.x_left_array() < 1.) * (self.curve.x_right_array() > 1.))
        exit_index = exit_indices[0][0] if len(exit_indices) > 0 else -1

        x_left = np.clip(self.curve.x_left_array()[enter_index:exit_index], 0., 1.)
        x_right = np.clip(self.curve.x_right_array()[enter_index:exit_index], 0., 1.)
        y = np.clip(self.curve.y_array()[enter_index:exit_index], 0., 1.)
        z = np.clip(self.curve.z_array()[enter_index:exit_index], 0., 1.)

        rectangle_count = y.size
        triangle_count = rectangle_count * 2
        vertex_count = triangle_count * 3

        if rectangle_count == 0:
            return

        if paint_node is None:
            paint_node = QSGGeometryNode()

            geometry = QSGGeometry(QSGGeometry.defaultAttributes_ColoredPoint2D(), vertex_count)
            geometry.setDrawingMode(QSGGeometry.DrawTriangles)
            paint_node.setGeometry(geometry)
            paint_node.setFlag(QSGNode.OwnsGeometry)

            material = QSGVertexColorMaterial()
            opaque_material = QSGVertexColorMaterial()
            paint_node.setMaterial(material)
            paint_node.setMaterial(opaque_material)
            paint_node.setFlag(QSGNode.OwnsMaterial)
            paint_node.setFlag(QSGNode.OwnsOpaqueMaterial)
        else:
            geometry = paint_node.geometry()
            geometry.allocate(vertex_count) # geometry will be marked as dirty below

        # ideally we would use geometry.vertexDataAsColoredPoint2D
        # but there is a bug with the returned sip.array
        # whose total size is not interpreted correctly
        # `memoryview(geometry.vertexDataAsPoint2D()).nbytes` does not take itemsize into account
        vertex_data = geometry.vertexData()

        # a custom structured data type that represents the vertex data is interpreted
        vertex_dtype = np.dtype([('x', np.float32), ('y', np.float32), ('r', np.ubyte), ('g', np.ubyte), ('b', np.ubyte), ('a', np.ubyte)])
        vertex_data.setsize(vertex_dtype.itemsize * vertex_count)

        vertices = np.frombuffer(vertex_data, dtype=vertex_dtype)

        baseline = self.curve.baseline() * self.height() + 0.*y
        h = (y - self.curve.baseline()) * self.height()

        if self.curve.curve_type == CurveType.SIGNAL:
            r = 0.*z
            g = (0.3 + 0.5*z) * 255
            b = 0.*z
        else:
            r = 255 + 0.*z
            g = 255 * (1. - z)
            b = 255 * (1. - z)

        a = 255 + 0.*y

        x_left_plot = np.clip(x_left, 0., 1.) * self.width()
        x_right_plot = np.clip(x_right, 0., 1.) * self.width()

        # first triangle
        vertices[0::6]['x'] = x_left_plot
        vertices[0::6]['y'] = baseline + h
        vertices[0::6]['r'] = r
        vertices[0::6]['g'] = g
        vertices[0::6]['b'] = b
        vertices[0::6]['a'] = a

        vertices[1::6]['x'] = x_right_plot
        vertices[1::6]['y'] = baseline + h
        vertices[1::6]['r'] = r
        vertices[1::6]['g'] = g
        vertices[1::6]['b'] = b
        vertices[1::6]['a'] = a

        vertices[2::6]['x'] = x_left_plot
        vertices[2::6]['y'] = baseline
        vertices[2::6]['r'] = r
        vertices[2::6]['g'] = g
        vertices[2::6]['b'] = b
        vertices[2::6]['a'] = a

        # second triangle
        vertices[3::6]['x'] = x_left_plot
        vertices[3::6]['y'] = baseline
        vertices[3::6]['r'] = r
        vertices[3::6]['g'] = g
        vertices[3::6]['b'] = b
        vertices[3::6]['a'] = a

        vertices[4::6]['x'] = x_right_plot
        vertices[4::6]['y'] = baseline
        vertices[4::6]['r'] = r
        vertices[4::6]['g'] = g
        vertices[4::6]['b'] = b
        vertices[4::6]['a'] = a

        vertices[5::6]['x'] = x_right_plot
        vertices[5::6]['y'] = baseline + h
        vertices[5::6]['r'] = r
        vertices[5::6]['g'] = g
        vertices[5::6]['b'] = b
        vertices[5::6]['a'] = a

        paint_node.markDirty(QSGNode.DirtyGeometry)
        paint_node.markDirty(QSGNode.DirtyMaterial)

        return paint_node
