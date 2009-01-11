#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2.0 as published by
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
from PyQt4 import Qt, QtCore
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *
import ImageQt
import Image
import numpy
from audiodata import *

class ImageRepaintHelper(Qt.QObject):
	def __init__(self, image, plot):
		Qt.QObject.__init__(self)
		self.image = image
		self.plot = plot

	def eventFilter(self, qobject, qevent):
		if qevent.type() == Qt.QEvent.Paint:
			canvas = self.plot.canvas()

			xMap = self.plot.canvasMap(self.image.xAxis())
			yMap = self.plot.canvasMap(self.image.yAxis())

#	    if canvas.testPaintAttribute(Qwt.QwtPlotCanvas.PaintCached) and canvas.paintCache() and not canvas.paintCache().isNull():
#		  cachePainter = Qt.QPainter(canvas.paintCache())
#		  cachePainter.translate(-canvas.contentsRect().x(), -canvas.contentsRect().y())
#
#		  cachePainter.setClipping(True)
#		  cachePainter.setClipRect(canvas.contentsRect())
#
#		  self.image.draw(cachePainter, xMap, yMap, canvas.contentsRect())

			painter = Qt.QPainter(canvas)
			#painter.setClipping(True)
			#painter.setClipRect(canvas.contentsRect())

			self.image.draw(painter, xMap, yMap, canvas.contentsRect())

			return True
		else:
			return False

class PlotImage(Qwt.QwtPlotItem):

	def __init__(self):
		Qwt.QwtPlotItem.__init__(self)

		self.parent_plot = None

		#self.rawspectrogram = RawSpectrogram()
		#self.freqscaledspectrogram = FreqScaledSpectrogram()
		self.canvasscaledspectrogram = CanvasScaledSpectrogram()

	def addData(self, xyzs, logfreqscale):
		#self.rawspectrogram.addData(xyzs)
		#self.freqscaledspectrogram.addData(xyzs, logfreqscale)
		self.canvasscaledspectrogram.addData(xyzs, logfreqscale)

	def draw(self, painter, xMap, yMap, rect):
		self.canvasscaledspectrogram.setcanvas_vsize(rect.height())
		self.canvasscaledspectrogram.setcanvas_hsize(rect.width())

		pixmap = self.canvasscaledspectrogram.getpixmap()
		offset = self.canvasscaledspectrogram.getpixmapoffset()
		painter.drawPixmap(rect.left(), rect.top(), pixmap,  offset,  0,  0,  0)

	def redraw(self):
		if self.parent_plot == None: self.parent_plot = self.plot()
		helper = ImageRepaintHelper(self,  self.parent_plot)
		canvas = self.parent_plot.canvas()
		canvas.installEventFilter(helper)
		noSystemBackground = canvas.testAttribute(QtCore.Qt.WA_NoSystemBackground)
		canvas.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
		canvas.repaint()
		canvas.setAttribute(QtCore.Qt.WA_NoSystemBackground, noSystemBackground)

	def erase(self):
		# set the data array to zero
		#self.rawspectrogram.erase()
		#self.freqscaledspectrogram.erase()
		self.canvasscaledspectrogram.erase()

class ImagePlot(Qwt.QwtPlot):

	def __init__(self, *args):
		Qwt.QwtPlot.__init__(self, *args)
		# set plot layout
		self.plotLayout().setMargin(0)
		self.plotLayout().setCanvasMargin(0)
		self.plotLayout().setAlignCanvasToScales(True)
		# set axis titles
		self.setAxisTitle(Qwt.QwtPlot.xBottom, 'time (s)')
		self.setAxisTitle(Qwt.QwtPlot.yLeft, 'frequency (Hz)')
		# attach a plot image
		self.plotImage = PlotImage()
		self.plotImage.attach(self)
		self.setlinfreqscale()
		
		# replot
		self.replot()
		
		#def setData(self, xyzs):
		#self.plotImage.setData(xyzs)
		#self.replot()

	def addData(self, xyzs):
		self.plotImage.addData(xyzs, self.logfreqscale)
		# we should just update the image here
		self.replot()
		#self.plotImage.redraw()

	def setlogfreqscale(self):
		self.plotImage.erase()
		self.logfreqscale = 1
		self.setAxisScaleEngine(Qwt.QwtPlot.yLeft, Qwt.QwtLog10ScaleEngine())
		self.setAxisScale(Qwt.QwtPlot.yLeft, 20., 22050.)
		self.replot()

	def setlinfreqscale(self):
		self.plotImage.erase()
		self.logfreqscale = 0
		self.setAxisScaleEngine(Qwt.QwtPlot.yLeft, Qwt.QwtLinearScaleEngine())
		self.setAxisScale(Qwt.QwtPlot.yLeft, 0., 22050.)
		self.replot()
