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

import sys
from ctypes import c_float, c_uint, c_void_p, sizeof

from PyQt5 import QtWidgets
from OpenGL import GL
from OpenGL.GL import shaders
import numpy as np


class QuadsItem:

    def __init__(self, r, g, b, *args):
        self.x1 = np.array([0.1, 0.5, 1.])
        self.x2 = np.array([0.5, 1., 2.])
        self.y = np.array([0., 0., 0.])
        self.y_int = np.array([0., 0., 0.])

        self.r = r
        self.g = g
        self.b = b

        self.transformed_x1 = self.x1
        self.transformed_x2 = self.x2

        self.need_transform = True

        self.baseline_transformed = False
        self.baseline = 0.

        self.vertices_data = np.array([], dtype=np.float32)

    def set_baseline_displayUnits(self, baseline):
        self.baseline_transformed = False
        self.baseline = baseline

    def set_baseline_dataUnits(self, baseline):
        self.baseline_transformed = True
        self.baseline = baseline

    def setData(self, x1, x2, y, y_int):
        if len(x1) != len(self.x1):
            self.need_transform = True

        self.x1 = x1
        self.x2 = x2
        self.y = y
        self.y_int = y_int

    def prepareQuadData(self, x, y, w, baseline, r, g, b):
        h = y - baseline
        y = baseline + 0.*y

        n = x.shape[0]

        # (1 quad = 2 triangles = 6 vertices) * (3 coordinates + 3 color coordinates)
        if self.vertices_data.shape != (n*6, 6):
            self.vertices_data = np.zeros((n*6, 6), dtype=np.float32)

        x_newaxis = x[:, np.newaxis]
        y_newaxis = y[:, np.newaxis]

        w_newaxis = w[:, np.newaxis]
        h_newaxis = h[:, np.newaxis]

        r_newaxis = r[:, np.newaxis]
        g_newaxis = g[:, np.newaxis]
        b_newaxis = b[:, np.newaxis]

        zero_newaxis = 0*x[:, np.newaxis]

        self.vertices_data[0::6, 0::6] = x_newaxis
        self.vertices_data[0::6, 1::6] = y_newaxis + h_newaxis
        self.vertices_data[0::6, 2::6] = zero_newaxis
        self.vertices_data[0::6, 3::6] = r_newaxis
        self.vertices_data[0::6, 4::6] = g_newaxis
        self.vertices_data[0::6, 5::6] = b_newaxis

        self.vertices_data[1::6, 0::6] = x_newaxis + w_newaxis
        self.vertices_data[1::6, 1::6] = y_newaxis + h_newaxis
        self.vertices_data[1::6, 2::6] = zero_newaxis
        self.vertices_data[1::6, 3::6] = r_newaxis
        self.vertices_data[1::6, 4::6] = g_newaxis
        self.vertices_data[1::6, 5::6] = b_newaxis

        self.vertices_data[2::6, 0::6] = x_newaxis
        self.vertices_data[2::6, 1::6] = y_newaxis
        self.vertices_data[2::6, 2::6] = zero_newaxis
        self.vertices_data[2::6, 3::6] = r_newaxis
        self.vertices_data[2::6, 4::6] = g_newaxis
        self.vertices_data[2::6, 5::6] = b_newaxis

        self.vertices_data[3::6, 0::6] = x_newaxis
        self.vertices_data[3::6, 1::6] = y_newaxis
        self.vertices_data[3::6, 2::6] = zero_newaxis
        self.vertices_data[3::6, 3::6] = r_newaxis
        self.vertices_data[3::6, 4::6] = g_newaxis
        self.vertices_data[3::6, 5::6] = b_newaxis

        self.vertices_data[4::6, 0::6] = x_newaxis + w_newaxis
        self.vertices_data[4::6, 1::6] = y_newaxis
        self.vertices_data[4::6, 2::6] = zero_newaxis
        self.vertices_data[4::6, 3::6] = r_newaxis
        self.vertices_data[4::6, 4::6] = g_newaxis
        self.vertices_data[4::6, 5::6] = b_newaxis

        self.vertices_data[5::6, 0::6] = x_newaxis + w_newaxis
        self.vertices_data[5::6, 1::6] = y_newaxis + h_newaxis
        self.vertices_data[5::6, 2::6] = zero_newaxis
        self.vertices_data[5::6, 3::6] = r_newaxis
        self.vertices_data[5::6, 4::6] = g_newaxis
        self.vertices_data[5::6, 5::6] = b_newaxis

    def transformUpdate(self):
        self.need_transform = True

    def glDraw(self, xMap, yMap, rect, vbo, shader_program):
        # transform the coordinates only when needed
        if self.need_transform:
            self.transformed_x1 = xMap.toScreen(self.x1)
            self.transformed_x2 = xMap.toScreen(self.x2)

            if xMap.log:
                self.transformed_x1, self.transformed_x2, n = pre_tree_rebin(self.transformed_x1, self.transformed_x2)
                self.n = [0] + n
                self.N = 0
                for i in range(len(self.n) - 1):
                    self.N += (self.n[i + 1] - self.n[i]) // 2 ** i

            self.need_transform = False

        # for easier reading
        x1 = self.transformed_x1
        x2 = self.transformed_x2

        if xMap.log:
            y = tree_rebin(self.y, self.n, self.N)
            y_int = tree_rebin(self.y_int, self.n, self.N)
        else:
            delta = x2[2] - x1[1]

            n = int(np.floor(1. / delta)) if delta > 0. else 0
            if n > 1:
                new_len = len(self.y) // n
                rest = len(self.y) - new_len * n

                if rest > 0:
                    new_y = self.y[:-rest]
                    new_y.shape = (new_len, n)
                    y = np.mean(new_y, axis=1)

                    new_y_int = self.y_int[:-rest]
                    new_y_int.shape = (new_len, n)
                    y_int = np.mean(new_y_int, axis=1)

                    x1 = x1[:-rest:n]
                    x2 = x2[n-1::n]
                else:
                    new_y = self.y.copy()
                    new_y.shape = (new_len, n)
                    y = np.mean(new_y, axis=1)

                    new_y_int = self.y_int.copy()
                    new_y_int.shape = (new_len, n)
                    y_int = np.mean(new_y_int, axis=1)

                    x1 = x1[::n]
                    x2 = x2[n-1::n]

            else:
                y = self.y
                y_int = self.y_int

        transformed_y = yMap.toScreen(y)

        r = self.r(y_int)
        g = self.g(y_int)
        b = self.b(y_int)

        if self.baseline_transformed:
            # used for dual channel response measurement
            baseline = yMap.toScreen(self.baseline)
        else:
            # used for single channel analysis
            baseline = self.baseline

        self.prepareQuadData(x1, transformed_y, x2 - x1, baseline, r, g, b)

        vbo.set_array(self.vertices_data)

        vbo.bind()
        try:
            GL.glEnableVertexAttribArray(0)
            GL.glEnableVertexAttribArray(1)
            stride = self.vertices_data.shape[-1]*sizeof(c_float)
            vertex_offset = c_void_p(0 * sizeof(c_float))
            color_offset = c_void_p(3 * sizeof(c_float))
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, vertex_offset)
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, color_offset)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.vertices_data.shape[0])
            GL.glDisableVertexAttribArray(0)
            GL.glDisableVertexAttribArray(1)
        finally:
            vbo.unbind()


def pre_tree_rebin(x1, x2):
    if len(x2) == 0:
        # enf of recursion !
        return x1, x2, 0

    bins = np.where(x2 - x1 >= 0.5)[0]

    if len(bins) == 0:
        n0 = len(x2)
    else:
        n0 = max(np.where(x2 - x1 >= 0.5)[0])

    # leave untouched the frequency bins that span more than half a pixel
    # and first make sure that what will be left can be decimated by two
    rest = len(x2) - n0 - ((len(x2) - n0) // 2) * 2

    n0 += rest

    x1_0 = x1[:n0]
    x2_0 = x2[:n0]

    # decimate the rest
    x1_2 = x1[n0::2]
    x2_2 = x2[n0 + 1::2]

    # recursive !!
    x1_2, x2_2, n2 = pre_tree_rebin(x1_2, x2_2)

    if n2 == 0.:
        n = [n0]
    else:
        n = [n0] + [i * 2 + n0 for i in n2]

    x1 = np.hstack((x1_0, x1_2))
    x2 = np.hstack((x2_0, x2_2))

    return x1, x2, n


def tree_rebin(y, ns, N):
    y2 = np.zeros(N)

    n = 0
    for i in range(len(ns) - 1):
        y3 = y[ns[i]:ns[i + 1]]
        d = 2 ** i
        l = len(y3) // d
        y3.shape = (l, d)

        # Note: the FFT spectrum is mostly used to identify frequency content
        # ans _peaks_ are particularly interesting (e.g. feedback frequencies)
        # so we display the _max_ instead of the mean of each bin
        # y3 = mean(y3, axis=1)
        # y3 = (y3[::2] + y3[1::2])*0.5

        y3 = np.max(y3, axis=1)

        y2[n:n + len(y3)] = y3
        n += l

    return y2
