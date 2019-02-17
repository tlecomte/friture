#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2019 Timothée Lecomte

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

from ctypes import c_float, c_uint, c_void_p, sizeof

import numpy as np
from PyQt5 import Qt


class LineItem:

    def __init__(self, *args):
        self.n = 0
        self.xMap = None
        self.yMap = None
        self.__color = Qt.QColor()
        self.__title = ""
        x = np.array([0., 1.])
        y = np.array([0., 0.])
        self.setData(x, y)

    def setColor(self, color):
        if self.__color != color:
            self.__color = color

            if self.n > 0:
                Ones = np.ones(self.n)
                r = self.color().red() / 255. * Ones
                g = self.color().green() / 255. * Ones
                b = self.color().blue() / 255. * Ones

                self.vertices_data[0::2, 2:] = np.dstack((0*r, r, g, b))
                self.vertices_data[1::2, 2:] = np.dstack((0*r, r, g, b))

    def color(self):
        return self.__color

    def setData(self, x, y):
        # make a copy so that pause works as expected
        self.x = np.array(x)
        self.y = np.array(y)

        n = x.shape[0] - 1
        if n != self.n:
            self.n = n

            Ones = np.ones(n)
            r = self.color().red() / 255. * Ones
            g = self.color().green() / 255. * Ones
            b = self.color().blue() / 255. * Ones

            # 2 vertices per segment * (3 coordinates + 3 color coordinates)
            self.vertices_data = np.zeros((n*2, 6), dtype=np.float32)
            self.vertices_data[0::2, 2:] = np.dstack((0*r, r, g, b))
            self.vertices_data[1::2, 2:] = np.dstack((0*r, r, g, b))

    def setTitle(self, title):
        self.__title = title

    def title(self):
        return self.__title

    def glDraw(self, xMap, yMap, rect, vbo, shader_program):
        x = xMap.toScreen(self.x)
        y = yMap.toScreen(self.y)

        self.vertices_data[0::2, :2] = np.dstack((x[:-1], y[:-1]))
        self.vertices_data[1::2, :2] = np.dstack((x[1:], y[1:]))

        if self.vertices_data.size == 0:
            return

        vbo.write(self.vertices_data)

        vbo.bind_to_uniform_block(0)
        try:
            pass
            # TODO convert to real shader !!
            # GL.glEnableVertexAttribArray(0)
            # GL.glEnableVertexAttribArray(1)
            # stride = self.vertices_data.shape[-1]*sizeof(c_float)
            # vertex_offset = c_void_p(0 * sizeof(c_float))
            # color_offset  = c_void_p(3 * sizeof(c_float))
            # GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, vertex_offset)
            # GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, color_offset)
            # GL.glDrawArrays(GL.GL_LINES, 0, self.vertices_data.shape[0])
            # GL.glDisableVertexAttribArray(0)
            # GL.glDisableVertexAttribArray(1)
        finally:
            vbo.orphan()
