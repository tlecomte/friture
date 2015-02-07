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

from PyQt4 import QtCore, Qt, QtGui
from numpy import log10, interp, linspace, sin, array
from friture.plotting.scaleWidget import VerticalScaleWidget, HorizontalScaleWidget
from friture.plotting.scaleDivision import ScaleDivision
from friture.plotting.coordinateTransform import CoordinateTransform
from friture.plotting.canvasWidget import CanvasWidget
from friture.plotting.legendWidget import LegendWidget

class CurveItem:
	def __init__(self, *args):
		self.x = array([0.])
		self.y = array([0.])
		self.canvas_width = 2
		self.need_transform = False
		self.yMap = None
		self.__color = Qt.QColor()
		self.__title = ""

	def setColor(self, color):
		if self.__color != color:
			self.__color = color

	def color(self):
		return self.__color

	def setData(self, x, y):
		self.x = x
		self.y = y

	def setTitle(self, title):
		self.__title = title

	def title(self):
		return self.__title

	def draw(self, painter, xMap, yMap, rect):
		# update the cache according to possibly new canvas dimensions
		h = rect.height()
		w = rect.width()
		if w <> self.canvas_width:
			self.canvas_width = w
			self.need_transform = True

		if self.need_transform:
			#self.x1 = xMap.toScreen(array(self.fl))
			self.need_transform = False

		x = xMap.toScreen(self.x)
		y = yMap.toScreen(self.y)

		# this should be maybe done by numpy instead
		points = QtGui.QPolygonF(map(lambda p: QtCore.QPointF(p[0], p[1]), zip(x, y)))

		painter.setPen(self.color())
		painter.drawPolyline(points)

class TimePlot(QtGui.QWidget):
	def __init__(self, parent, logger):
		super(TimePlot, self).__init__()

		# store the logger instance
		self.logger = logger

		self.verticalScaleDivision = ScaleDivision(-1, 1, 100)
		self.verticalScaleTransform = CoordinateTransform(-1, 1, 100, 0, 0)

		self.verticalScale = VerticalScaleWidget(self, self.verticalScaleDivision, self.verticalScaleTransform)
		self.verticalScale.setTitle("Signal")

		self.horizontalScaleDivision = ScaleDivision(-1, 1, 100)
		self.horizontalScaleTransform = CoordinateTransform(-1, 1, 100, 0, 0)

		self.horizontalScale = HorizontalScaleWidget(self, self.horizontalScaleDivision, self.horizontalScaleTransform)
		self.horizontalScale.setTitle("Time (ms)")

		self.canvasWidget = CanvasWidget(self, self.verticalScaleTransform, self.horizontalScaleTransform)
		self.canvasWidget.setTrackerFormatter(lambda x, y: "%.3g ms, %.3g" %(x, y))

		self.legendWidget = LegendWidget(self, self.canvasWidget)

		plotLayout = QtGui.QGridLayout()
		plotLayout.setSpacing(0)
		plotLayout.setContentsMargins(0, 0, 0, 0)
		plotLayout.addWidget(self.verticalScale, 0, 0)
		plotLayout.addWidget(self.canvasWidget, 0, 1)
		plotLayout.addWidget(self.horizontalScale, 1, 1)
		plotLayout.addWidget(self.legendWidget, 0, 2)

		self.setLayout(plotLayout)

		self.needfullreplot = False

		self.curve = CurveItem()
		self.curve.setColor(Qt.Qt.red)
		# gives a title to the curve for the legend
		self.curve.setTitle("Ch1")
		self.canvasWidget.attach(self.curve)

		self.curve2 = CurveItem()
		self.curve2.setColor(Qt.Qt.blue)
		# gives a title to the curve for the legend
		self.curve2.setTitle("Ch2")
		# self.curve2 will be attached when needed

		#need to replot here for the size Hints to be computed correctly (depending on axis scales...)
		self.update()

		self.xmin = 0.
		self.xmax = 1.

		self.canvas_width = 0

		self.dual_channel = False

	def setdata(self, x, y):
		if self.canvas_width <> self.canvasWidget.width():
			self.logger.push("timeplot : changed canvas width")
			self.canvas_width = self.canvasWidget.width()
			self.update_xscale()

		if self.dual_channel:
			self.dual_channel = False
			self.canvasWidget.detach(self.curve2)
			# disable the legend, useless when one channel is active
			self.legendWidget.hide()
			self.needfullreplot = True
			self.update()

		x_ms =  1e3*x
		if self.xmax <> x_ms[-1]:
			self.logger.push("timeplot : changing x max")
			self.xmax = x_ms[-1]
			self.settimerange(self.xmin, self.xmax)
			self.update_xscale()
			self.needfullreplot = True
		if self.xmin <> x_ms[0]:
			self.logger.push("timeplot : changing x min")
			self.xmin = x_ms[0]
			self.settimerange(self.xmin, self.xmax)
			self.update_xscale()
			self.needfullreplot = True

		y_interp = interp(self.xscaled, x_ms, y)
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

			self.canvasWidget.setGrid(array(self.horizontalScaleDivision.majorTicks()),
										array(self.horizontalScaleDivision.minorTicks()),
										array(self.verticalScaleDivision.majorTicks()),
										array(self.verticalScaleDivision.minorTicks())
										)

		self.canvasWidget.update()

	# redraw when the widget is resized to update coordinates transformations
	def resizeEvent(self, event):
		self.needfullreplot = True
		self.draw()

	def setdataTwoChannels(self, x, y, y2):
		if self.canvas_width <> self.canvasWidget.width():
			self.logger.push("timeplot : changed canvas width")
			self.canvas_width = self.canvasWidget.width()
			self.update_xscale()

		if not self.dual_channel:
			self.dual_channel = True
			self.canvasWidget.attach(self.curve2)
			# enable the legend to discrimate between the two channels
			self.legendWidget.show()
			self.needfullreplot = True
			self.update()

		x_ms =  1e3*x
		if self.xmax <> x_ms[-1]:
			self.logger.push("timeplot : changing x max")
			self.xmax = x_ms[-1]
			self.settimerange(self.xmin, self.xmax)
			self.update_xscale()
			self.needfullreplot = True
		if self.xmin <> x_ms[0]:
			self.logger.push("timeplot : changing x min")
			self.xmin = x_ms[0]
			self.settimerange(self.xmin, self.xmax)
			self.update_xscale()
			self.needfullreplot = True

		#y_interp = interp(self.xscaled, x_ms, y)
		#y_interp2 = interp(self.xscaled, x_ms, y2)
		#ClassPlot.setdata(self, self.xscaled, y_interp)
		#self.curve2.setData(self.xscaled, y_interp2)
		self.curve.setData(x_ms, y)
		self.curve2.setData(x_ms, y2)

		self.draw()

	def update_xscale(self):
		self.xscaled = linspace(self.xmin, self.xmax, self.canvas_width)

	def settimerange(self, min, max):
		self.horizontalScaleTransform.setRange(min, max)
		self.horizontalScaleDivision.setRange(min, max)

		# notify that sizeHint has changed (this should be done with a signal emitted from the scale division to the scale bar)
		self.horizontalScale.scaleBar.updateGeometry()

		self.needfullreplot = True
		self.update()
