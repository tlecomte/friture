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

import numpy
from PyQt4 import QtGui, QtCore, Qt
import PyQt4.Qwt5 as Qwt

class ImageRepaintHelper(Qt.QObject):
	def __init__(self, curve):
		Qt.QObject.__init__(self)
		self.curve = curve

	def eventFilter(self, qobject, qevent):
		if qevent.type() == Qt.QEvent.Paint:
			plot = self.curve.plot()

			canvas = plot.canvas()
	
			xMap = plot.canvasMap(self.curve.xAxis())
			yMap = plot.canvasMap(self.curve.yAxis())

#	    if canvas.testPaintAttribute(Qwt.QwtPlotCanvas.PaintCached) and canvas.paintCache() and not canvas.paintCache().isNull():
#		  cachePainter = Qt.QPainter(canvas.paintCache())
#		  cachePainter.translate(-canvas.contentsRect().x(),
#		    -canvas.contentsRect().y())
#
#		  self.curve.draw(cachePainter, xMap, yMap, canvas.contentsRect())

			painter = Qt.QPainter(canvas)
			
			painter.setClipping(True)
			painter.setClipRect(canvas.contentsRect())
			
			self.curve.draw(painter, xMap, yMap, canvas.contentsRect())
			
			return True
		else:
			return False
	
class ClassPlot(Qwt.QwtPlot):

	def __init__(self, *args):
		Qwt.QwtPlot.__init__(self, *args)

		# set plot layout
		self.plotLayout().setMargin(0)
		self.plotLayout().setCanvasMargin(0)
		self.plotLayout().setAlignCanvasToScales(True)

		self.setAxisScale(Qwt.QwtPlot.yLeft, -1., 1.)

		# insert a few curves
		self.curve = ClassCurve()
		self.curve.setPen(QtGui.QPen(Qt.Qt.red))
		#self.curve.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
		self.curve.attach(self)
		
		# make a Numeric array for the horizontal data
		x = numpy.arange(0.0, 10.0, 0.1)

		# initialize the data
		self.curve.setData(x, numpy.sin(x))

		# replot
		self.replot()

	def setdata(self,x,y):
		self.curve.setData(x,y)
		#self.redraw(self.curve)
		self.replot()

#	def redraw(self, curve):
#		helper = ImageRepaintHelper(curve)
#		canvas = self.canvas()
#		canvas.installEventFilter(helper)
#		noSystemBackground = canvas.testAttribute(QtCore.Qt.WA_NoSystemBackground)
#		canvas.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)
#		canvas.repaint()
#		canvas.setAttribute(QtCore.Qt.WA_NoSystemBackground, noSystemBackground)

class ClassCurve(Qwt.QwtPlotCurve):

	def __init__(self, *args):
		Qwt.QwtPlotCurve.__init__(self, *args)
