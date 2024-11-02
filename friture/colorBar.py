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

from PyQt5.QtQuick import QQuickItem, QSGGeometryNode, QSGGeometry, QSGNode, QSGVertexColorMaterial

from friture.plotting import generated_cmrmap

class ColorBar(QQuickItem):

    def __init__(self, parent = None):
        super().__init__(parent)

        self._cmap = generated_cmrmap.CMAP

        self.setFlag(QQuickItem.ItemHasContents, True)

    def updatePaintNode(self, paint_node, update_data):

        if self.width() == 0:
            return

        rectangle_count = int(self.height())
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

        color_count = self._cmap.shape[0]

        y = np.arange(0, self.height())
        h = 1.
        yNorm = 1. - y / self.height()
        color_index = (yNorm * (color_count - 1)).astype(int)
        r = self._cmap[color_index, 0] * 255
        g = self._cmap[color_index, 1] * 255
        b = self._cmap[color_index, 2] * 255
        a = 255 + 0.*y

        x_left = 0.*y
        x_right = self.width() + 0.*y

        # first triangle
        vertices[0::6]['x'] = x_left
        vertices[0::6]['y'] = y + h
        vertices[0::6]['r'] = r
        vertices[0::6]['g'] = g
        vertices[0::6]['b'] = b
        vertices[0::6]['a'] = a

        vertices[1::6]['x'] = x_right
        vertices[1::6]['y'] = y + h
        vertices[1::6]['r'] = r
        vertices[1::6]['g'] = g
        vertices[1::6]['b'] = b
        vertices[1::6]['a'] = a

        vertices[2::6]['x'] = x_left
        vertices[2::6]['y'] = y
        vertices[2::6]['r'] = r
        vertices[2::6]['g'] = g
        vertices[2::6]['b'] = b
        vertices[2::6]['a'] = a

        # second triangle
        vertices[3::6]['x'] = x_left
        vertices[3::6]['y'] = y
        vertices[3::6]['r'] = r
        vertices[3::6]['g'] = g
        vertices[3::6]['b'] = b
        vertices[3::6]['a'] = a

        vertices[4::6]['x'] = x_right
        vertices[4::6]['y'] = y
        vertices[4::6]['r'] = r
        vertices[4::6]['g'] = g
        vertices[4::6]['b'] = b
        vertices[4::6]['a'] = a

        vertices[5::6]['x'] = x_right
        vertices[5::6]['y'] = y + h
        vertices[5::6]['r'] = r
        vertices[5::6]['g'] = g
        vertices[5::6]['b'] = b
        vertices[5::6]['a'] = a

        paint_node.markDirty(QSGNode.DirtyGeometry)
        paint_node.markDirty(QSGNode.DirtyMaterial)

        return paint_node
