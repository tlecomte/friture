#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

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
import logging

from PyQt5 import Qt, QtGui, QtWidgets
import numpy as np
from friture.plotting.scaleWidget import VerticalScaleWidget, HorizontalScaleWidget
from friture.plotting.scaleDivision import ScaleDivision
from friture.plotting.coordinateTransform import CoordinateTransform
from friture.plotting.glCanvasWidget import GlCanvasWidget
from friture.plotting.legendWidget import LegendWidget

try:
    from OpenGL import GL
except ImportError:
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None, "OpenGL hellogl",
                                   "PyOpenGL must be installed to run this example.")
    sys.exit(1)

from OpenGL.GL import shaders
from ctypes import sizeof, c_float, c_void_p, c_uint

class CurveItem:

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

        vbo.set_array(self.vertices_data)

        vbo.bind()
        try:
            GL.glEnableVertexAttribArray(0)
            GL.glEnableVertexAttribArray(1)
            stride = self.vertices_data.shape[-1]*sizeof(c_float)
            vertex_offset = c_void_p(0 * sizeof(c_float))
            color_offset  = c_void_p(3 * sizeof(c_float))
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, vertex_offset)
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, color_offset)
            GL.glDrawArrays(GL.GL_LINES, 0, self.vertices_data.shape[0])
            GL.glDisableVertexAttribArray(0)
            GL.glDisableVertexAttribArray(1)
        finally:
            vbo.unbind()


class TimePlot(QtWidgets.QWidget):

    def __init__(self, parent):
        super(TimePlot, self).__init__()

        self.logger = logging.getLogger(__name__)

        self.verticalScaleDivision = ScaleDivision(-1, 1, 100)
        self.verticalScaleTransform = CoordinateTransform(-1, 1, 100, 0, 0)

        self.verticalScale = VerticalScaleWidget(self, self.verticalScaleDivision, self.verticalScaleTransform)
        self.verticalScale.setTitle("Signal")

        self.horizontalScaleDivision = ScaleDivision(-1, 1, 100)
        self.horizontalScaleTransform = CoordinateTransform(-1, 1, 100, 0, 0)

        self.horizontalScale = HorizontalScaleWidget(self, self.horizontalScaleDivision, self.horizontalScaleTransform)
        self.horizontalScale.setTitle("Time (ms)")

        self.canvasWidget = GlCanvasWidget(self, self.verticalScaleTransform, self.horizontalScaleTransform)
        self.canvasWidget.setTrackerFormatter(lambda x, y: "%.3g ms, %.3g" % (x, y))

        self.legendWidget = LegendWidget(self, self.canvasWidget)

        plotLayout = QtWidgets.QGridLayout()
        plotLayout.setSpacing(0)
        plotLayout.setContentsMargins(0, 0, 0, 0)
        plotLayout.addWidget(self.verticalScale, 0, 0)
        plotLayout.addWidget(self.canvasWidget, 0, 1)
        plotLayout.addWidget(self.horizontalScale, 1, 1)
        plotLayout.addWidget(self.legendWidget, 0, 2)

        self.setLayout(plotLayout)
        self.legendWidget.hide()

        self.needfullreplot = False

        self.curve = CurveItem()
        self.curve.setColor(QtGui.QColor(Qt.Qt.red))
        # gives a title to the curve for the legend
        self.curve.setTitle("Ch1")
        self.canvasWidget.attach(self.curve)

        self.curve2 = CurveItem()
        self.curve2.setColor(QtGui.QColor(Qt.Qt.blue))
        # gives a title to the curve for the legend
        self.curve2.setTitle("Ch2")
        # self.curve2 will be attached when needed

        # need to replot here for the size Hints to be computed correctly (depending on axis scales...)
        self.update()

        self.xmin = 0.
        self.xmax = 1.

        self.canvas_width = 0

        self.dual_channel = False

        self.paused = False

        self.canvasWidget.resized.connect(self.canvasResized)

    def setdata(self, x, y):
        if self.canvas_width != self.canvasWidget.width():
            self.logger.info("timeplot : changed canvas width")
            self.canvas_width = self.canvasWidget.width()
            self.update_xscale()

        if self.dual_channel:
            self.dual_channel = False
            self.canvasWidget.detach(self.curve2)
            # disable the legend, useless when one channel is active
            self.legendWidget.hide()
            # the canvas reisze event will trigger a full replot

        if self.xmax != x[-1]:
            self.logger.info("timeplot : changing x max")
            self.xmax = x[-1]
            self.settimerange(self.xmin, self.xmax)
            self.update_xscale()
            self.needfullreplot = True
        if self.xmin != x[0]:
            self.logger.info("timeplot : changing x min")
            self.xmin = x[0]
            self.settimerange(self.xmin, self.xmax)
            self.update_xscale()
            self.needfullreplot = True

        if not self.paused:
            y_interp = np.interp(self.xscaled, x, y)
            self.curve.setData(self.xscaled, y_interp)

        self.draw()

    def draw(self):
        if self.needfullreplot:
            self.needfullreplot = False

            self.verticalScaleDivision.setLength(self.canvasWidget.height())
            self.verticalScaleTransform.setLength(self.canvasWidget.height())
            startBorder, endBorder = self.verticalScale.spacingBorders()
            self.verticalScaleTransform.setBorders(startBorder, endBorder)

            self.verticalScale.update()

            self.horizontalScaleDivision.setLength(self.canvasWidget.width())
            self.horizontalScaleTransform.setLength(self.canvasWidget.width())
            startBorder, endBorder = self.horizontalScale.spacingBorders()
            self.horizontalScaleTransform.setBorders(startBorder, endBorder)

            self.horizontalScale.update()

            self.canvasWidget.setGrid(np.array(self.horizontalScaleDivision.majorTicks()),
                                      np.array(self.horizontalScaleDivision.minorTicks()),
                                      np.array(self.verticalScaleDivision.majorTicks()),
                                      np.array(self.verticalScaleDivision.minorTicks()))

    def pause(self):
        self.paused = True
        self.canvasWidget.pause()

    def restart(self):
        self.paused = False
        self.canvasWidget.restart()

    # redraw when the widget is resized to update coordinates transformations
    # this is done instead of resizeEvent because the canvas can be resized independently of the whole plot (because the legend can disappear)
    def canvasResized(self, canvasWidth, canvasHeight):
        self.needfullreplot = True
        self.draw()

    def setdataTwoChannels(self, x, y, y2):
        if self.canvas_width != self.canvasWidget.width():
            self.logger.info("timeplot : changed canvas width")
            self.canvas_width = self.canvasWidget.width()
            self.update_xscale()

        if not self.dual_channel:
            self.dual_channel = True
            self.canvasWidget.attach(self.curve2)
            # enable the legend to discrimate between the two channels
            self.legendWidget.show()
            # the canvas reisze event will trigger a full replot

        if self.xmax != x[-1]:
            self.logger.info("timeplot : changing x max")
            self.xmax = x[-1]
            self.settimerange(self.xmin, self.xmax)
            self.update_xscale()
            self.needfullreplot = True
        if self.xmin != x[0]:
            self.logger.info("timeplot : changing x min")
            self.xmin = x[0]
            self.settimerange(self.xmin, self.xmax)
            self.update_xscale()
            self.needfullreplot = True

        if not self.paused:
            # y_interp = np.interp(self.xscaled, x, y)
            # y_interp2 = np.interp(self.xscaled, x, y2)
            # ClassPlot.setdata(self, self.xscaled, y_interp)
            # self.curve2.setData(self.xscaled, y_interp2)
            self.curve.setData(x, y)
            self.curve2.setData(x, y2)

        self.draw()

    def update_xscale(self):
        self.xscaled = np.linspace(self.xmin, self.xmax, self.canvas_width)

    def settimerange(self, time_min, time_max):
        self.horizontalScaleTransform.setRange(time_min, time_max)
        self.horizontalScaleDivision.setRange(time_min, time_max)

        # notify that sizeHint has changed (this should be done with a signal emitted from the scale division to the scale bar)
        self.horizontalScale.scaleBar.updateGeometry()

        self.needfullreplot = True
        self.draw()

    def setverticalrange(self, v_min, v_max):
        self.verticalScaleTransform.setRange(v_min, v_max)
        self.verticalScaleDivision.setRange(v_min, v_max)

        # notify that sizeHint has changed (this should be done with a signal emitted from the scale division to the scale bar)
        self.verticalScale.scaleBar.updateGeometry()

        self.needfullreplot = True
        self.draw()

    def setverticaltitle(self, title):
        self.verticalScale.setTitle(title)

    def sethorizontaltitle(self, title):
        self.horizontalScale.setTitle(title)

    def setTrackerFormatter(self, formatter):
        self.canvasWidget.setTrackerFormatter(formatter)
