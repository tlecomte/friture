#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth￩e Lecomte

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

import classplot
import PyQt4.Qwt5 as Qwt
from PyQt4 import QtCore, Qt, QtGui
from numpy import zeros, ones, log10, linspace, logspace, interp, log2, histogram
from log2_scale_engine import QwtLog10ScaleEngine
import log2scale

# The peak decay rates (magic goes here :).
PEAK_DECAY_RATE = 1.0 - 3E-6
# Number of cycles the peak stays on hold before fall-off.
PEAK_FALLOFF_COUNT = 32 # default : 16

class FreqScaleDraw(Qwt.QwtScaleDraw):
	def __init__(self, *args):
		Qwt.QwtScaleDraw.__init__(self, *args)

	def label(self, value):
		#if value >= 1e3:
		#	label = "%gk" %(value/1e3)
		#else:
		label = "%d" %(value)
		return Qwt.QwtText(label)

class picker(Qwt.QwtPlotPicker):
	def __init__(self, *args):
		Qwt.QwtPlotPicker.__init__(self, *args)
		
	def trackerText(self, pos):
		pos2 = self.invTransform(pos)
		return Qwt.QwtText("%d Hz, %.1f dB" %(pos2.x(), pos2.y()))

	def drawTracker(self, painter):
		textRect = self.trackerRect(painter.font())
		if not textRect.isEmpty():
		  	   label = self.trackerText(self.trackerPosition())
		  	   if not label.isEmpty():
		  	   	   painter.save()
		  	   	   painter.setPen(Qt.Qt.NoPen)
		  	   	   painter.setBrush(Qt.Qt.white)
		  	   	   painter.drawRect(textRect)
		  	   	   painter.setPen(Qt.Qt.black)
		  	   	   #painter->setRenderHint(QPainter::TextAntialiasing, false);
		  	   	   label.draw(painter, textRect)
		  	   	   painter.restore()

class HistogramItem(Qwt.QwtPlotItem):

	Auto = 0
	Xfy = 1
	
	def __init__(self, *args):
		Qwt.QwtPlotItem.__init__(self, *args)
		self.__attributes = HistogramItem.Auto
		self.__data = Qwt.QwtIntervalData()
		self.__color = Qt.QColor()
		self.__reference = 0.0
		self.setItemAttribute(Qwt.QwtPlotItem.AutoScale, True)
		self.setItemAttribute(Qwt.QwtPlotItem.Legend, True)
		self.setZ(20.0)
		
		self.rect = QtCore.QRect()
		self.canvas_height = 0
		
		self.pixmap = QtGui.QPixmap()

	def setData(self, data):
		self.__data = data
		self.itemChanged()

	def data(self):
		return self.__data

	def setColor(self, color):
		if self.__color != color:
			self.__color = color
			self.itemChanged()

	def color(self):
		return self.__color

	def boundingRect(self):
		result = self.__data.boundingRect()
		if not result.isvalid():
			return result
		if self.testHistogramAttribute(HistogramItem.Xfy):
			result = Qwt.QwtDoubleRect(result.y(), result.x(),
									   result.height(), result.width())
			if result.left() > self.baseline():
				result.setLeft(self.baseline())
			elif result.right() < self.baseline():
				result.setRight(self.baseline())
		else:
			if result.bottom() < self.baseline():
				result.setBottom(self.baseline())
			elif result.top() > self.baseline():
				result.setTop(self.baseline())
		return result

	def rtti(self):
		return Qwt.QwtPlotItem.PlotHistogram

	def draw(self, painter, xMap, yMap, rect):
		self.canvas_height = rect.height()
		
		iData = self.data()
		
		y0 = yMap.transform(self.baseline())
		
		for i in range(iData.size()):
			x1 = xMap.transform(iData.interval(i).minValue())
			x2 = xMap.transform(iData.interval(i).maxValue())-1
			y2 = yMap.transform(iData.value(i))
				
			self.drawBar(painter, Qt.Qt.Vertical, Qt.QRect(x1, y0, x2-x1, y2-y0))

	def setBaseline(self, reference):
		if self.baseline() != reference:
			self.__reference = reference
			self.itemChanged()
	
	def baseline(self,):
		return self.__reference

	def setHistogramAttribute(self, attribute, on = True):
		if self.testHistogramAttribute(attribute):
			return

		if on:
			self.__attributes |= attribute
		else:
			self.__attributes &= ~attribute

		self.itemChanged()

	def testHistogramAttribute(self, attribute):
		return bool(self.__attributes & attribute) 

	# For a dramatic speedup, the bars are cached instead of drawn from scratch each time
	def update_pixmap(self, rect):
		r = rect.translated(0,0)
		r.setHeight(self.canvas_height)
		r.moveLeft(0)
		r.moveTop(0)
		
		self.rect = r.translated(0,0)
		
		color = QtGui.QColor(self.color())
		
		self.pixmap = QtGui.QPixmap(r.width()+1, r.height()+1)
		self.pixmap.fill(color)
		painter = QtGui.QPainter(self.pixmap)
		if rect.width() > 3:
			self.drawBarDecoration(painter, r)
		
		r.setWidth(r.width() - 1)
		self.pixmap_l = QtGui.QPixmap(r.width()+1, r.height()+1)
		self.pixmap_l.fill(color)
		painter = QtGui.QPainter(self.pixmap_l)
		if rect.width() > 3:
			self.drawBarDecoration(painter, r)
		
		r.setWidth(r.width() + 2)
		self.pixmap_h = QtGui.QPixmap(r.width()+1, r.height()+1)
		self.pixmap_h.fill(color)
		painter = QtGui.QPainter(self.pixmap_h)
		if rect.width() > 3:
			self.drawBarDecoration(painter, r)
		
	def drawBarDecoration(self, painter, r):
		color = QtGui.QColor(self.color())
		factor = 125
		light = color.lighter(factor)
		dark = color.darker(factor)
		
		painter.setBrush(Qt.Qt.NoBrush)

		#horizontal line
		painter.setPen(Qt.QPen(light, 2))
		painter.drawLine(r.left()+1, r.top()+2, r.right()+1, r.top()+2)

		#horizontal line
		painter.setPen(Qt.QPen(dark, 2))
		painter.drawLine(r.left()+1, r.bottom(), r.right()+1, r.bottom())

		#vertical line
		painter.setPen(Qt.QPen(light, 1))
		painter.drawLine(r.left(), r.top() + 1, r.left(), r.bottom())
		painter.drawLine(r.left()+1, r.top()+2, r.left()+1, r.bottom()-1)
		
		#vertical line
		painter.setPen(Qt.QPen(dark, 1))
		painter.drawLine(r.right()+1, r.top()+1, r.right()+1, r.bottom())
		painter.drawLine(r.right(), r.top()+2, r.right(), r.bottom()-1)
		
	def drawBar(self, painter, orientation, rect):
		# If width() < 0 the function swaps the left and right corners, and it swaps the top and bottom corners if height() < 0.
		rect = rect.normalized()
		
		if rect.width() < self.rect.width() - 1 or rect.width() > self.rect.width() + 1 or self.canvas_height <> self.rect.height():	
			self.update_pixmap(rect)
		
		if rect.width() == self.rect.width():
			painter.drawPixmap(rect.left(), rect.top(), self.pixmap)
		elif rect.width() == self.rect.width() + 1:
			painter.drawPixmap(rect.left(), rect.top(), self.pixmap_h)
		elif rect.width() == self.rect.width() - 1:
			painter.drawPixmap(rect.left(), rect.top(), self.pixmap_l)
		else:
			raise StandardError("Histplot bar width error!!")

class HistogramPeakItem(Qwt.QwtPlotItem):

	Auto = 0
	Xfy = 1
	
	def __init__(self, *args):
		Qwt.QwtPlotItem.__init__(self, *args)
		self.__attributes = HistogramItem.Auto
		self.fl = [0.]
		self.fh = [0.]
		self.peaks = [0.]
		self.__color = Qt.QColor()
		self.__reference = 0.0
		self.setItemAttribute(Qwt.QwtPlotItem.AutoScale, True)
		self.setItemAttribute(Qwt.QwtPlotItem.Legend, True)
		self.setZ(20.0)

	def setData(self, fl, fh, peaks):
		self.fl = fl
		self.fh = fh
		self.peaks = peaks
		self.itemChanged()

	def data(self):
		return [self.fl, self.fh, self.peaks]

	def setColor(self, color):
		if self.__color != color:
			self.__color = color
			self.itemChanged()

	def color(self):
		return self.__color

	def draw(self, painter, xMap, yMap, rect):
		self.canvas_height = rect.height()
		
		color = QtGui.QColor(self.color())
		factor = 125
		#light = color.lighter(factor)
		dark = color.darker(factor)

		#horizontal line
		painter.setBrush(Qt.Qt.NoBrush)
		painter.setPen(Qt.QPen(dark, 2))
		
		#for i in range(iData.size()):
		for flow, fhigh, peak in zip(self.fl, self.fh, self.peaks):
			x1 = xMap.transform(flow)+1
			x2 = xMap.transform(fhigh)-1
			y = yMap.transform(peak)
			
			painter.drawLine(x1, y, x2, y)

	def setBaseline(self, reference):
		if self.baseline() != reference:
			self.__reference = reference
			self.itemChanged()
	
	def baseline(self,):
		return self.__reference

	def setHistogramAttribute(self, attribute, on = True):
		if self.testHistogramAttribute(attribute):
			return

		if on:
			self.__attributes |= attribute
		else:
			self.__attributes &= ~attribute

		self.itemChanged()

	def testHistogramAttribute(self, attribute):
		return bool(self.__attributes & attribute) 

class HistPlot(Qwt.QwtPlot):
	def __init__(self, parent, logger):
		Qwt.QwtPlot.__init__(self)

		# store the logger instance
		self.logger = logger

		# we do not need caching
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintCached, False)
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintPacked, False)

		self.setAxisScale(Qwt.QwtPlot.yLeft, -140., 0.)
		xtitle = Qwt.QwtText('Frequency (Hz)')
		xtitle.setFont(QtGui.QFont(8))
		self.setAxisTitle(Qwt.QwtPlot.xBottom, xtitle)
		# self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Frequency (Hz)')
		ytitle = Qwt.QwtText('PSD (dB A)')
		ytitle.setFont(QtGui.QFont(8))
		self.setAxisTitle(Qwt.QwtPlot.yLeft, ytitle)
		# self.setAxisTitle(Qwt.QwtPlot.yLeft, 'PSD (dB)')

		# attach a grid
		grid = Qwt.QwtPlotGrid()
		grid.enableX(False)
		grid.setMajPen(Qt.QPen(Qt.QPen(Qt.Qt.gray)))
		grid.setMinPen(Qt.QPen(Qt.QPen(Qt.Qt.lightGray)))
		grid.attach(self)

		self.needfullreplot = False

		self.setAxisScale(Qwt.QwtPlot.xBottom, 63., 16000.)
		#self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, )
		
		self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLog10ScaleEngine())
		
		#try:
		#	s = Qwt.QwtLog10ScaleEngine()
		#	s.autoScale(1,1.,1.)
		#except:
		#	print "The loaded PyQwt library has buggy QwtScaleEngine (and friends) SIP declarations"
		#	print "... use a log10 scale engine instead of a log2 scale engine"
		#	self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLog10ScaleEngine())
		#else:
		#	self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, log2scale.CustomScaleEngine())
		
		self.setAxisScaleDraw(Qwt.QwtPlot.xBottom, FreqScaleDraw())
		
		self.paint_time = 0.

		# picker used to display coordinates when clicking on the canvas
		self.picker = picker(Qwt.QwtPlot.xBottom,
							   Qwt.QwtPlot.yLeft,
							   Qwt.QwtPicker.PointSelection,
							   Qwt.QwtPlotPicker.CrossRubberBand,
							   Qwt.QwtPicker.ActiveOnly,
							   self.canvas())
		
		# insert an additional curve for the peak
		self.curve_peak = HistogramPeakItem()
		self.curve_peak.setColor(Qt.Qt.blue)
		self.curve_peak.attach(self)
		self.peak = zeros((1,))
		self.peakHold = 0
		self.peakDecay = PEAK_DECAY_RATE
		
		self.histogram = HistogramItem()
		self.histogram.setColor(Qt.Qt.darkGreen)
		self.histogram.setBaseline(-200.)
		
		numValues = 20
		intervals = []
		values = Qwt.QwtArrayDouble(numValues)

		import random

		pos = 0.0
		for i in range(numValues):
			width = 5 + random.randint(0, 4)
			value = random.randint(0, 99)
			intervals.append(Qwt.QwtDoubleInterval(pos, pos+width))
			values[i] = value
			pos += width

		self.histogram.setData(Qwt.QwtIntervalData(intervals, values))
		self.histogram.attach(self)
		
		self.cached_canvas = self.canvas()
		
		# set the size policy to "Preferred" to allow the widget to be shrinked under the default size, which is quite big
		self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)

	def setdata(self, fl, fh, y):
		intervals = []
		values = Qwt.QwtArrayDouble(len(y))
		i = 0
		
		for flow, fhigh, value in zip(fl, fh, y):
			interval = Qwt.QwtDoubleInterval(flow, fhigh)
			intervals += [interval]
			values[i] = value
			i += 1
		
		self.histogram.setData(Qwt.QwtIntervalData(intervals, values))
		
		self.compute_peaks(y)
		self.curve_peak.setData(fl, fh, self.peak)
		
		if self.needfullreplot:
			self.needfullreplot = False
			self.replot()
		else:
			# self.replot() would call updateAxes() which is dead slow (probably because it
			# computes label sizes); instead, let's just ask Qt to repaint the canvas next time
			# This works because we disable the cache
			self.cached_canvas.update()

	def compute_peaks(self, y):
		if len(self.peak) <> len(y):
			y_ones = ones(y.shape)
			self.peak = y_ones*(-500.)
			self.peakHold = zeros(y.shape)
			self.dBdecay = y_ones * 20. * log10(PEAK_DECAY_RATE)

		mask1 = (self.peak < y)
		mask2 = (-mask1) * (self.peakHold > (PEAK_FALLOFF_COUNT - 1.))
		mask2_a = mask2 * (self.peak + self.dBdecay < y)
		mask2_b = mask2 * (self.peak + self.dBdecay >= y)

		self.peak[mask1] = y[mask1]
		self.peak[mask2_a] = y[mask2_a]
		self.peak[mask2_b] = self.peak[mask2_b] + self.dBdecay[mask2_b]
		
		self.dBdecay[mask1] = 20. * log10(PEAK_DECAY_RATE)
		self.dBdecay[mask2_b] = 2 * self.dBdecay[mask2_b]
		
		self.peakHold[mask1] = 0
		self.peakHold += 1
	
	def setspecrange(self, min, max):
		self.setAxisScale(Qwt.QwtPlot.yLeft, min, max)
		self.needfullreplot = True
	
	def setweighting(self, weighting):
		if weighting is 0:
			title = "PSD (dB)"
		elif weighting is 1:
			title = "PSD (dB A)"
		elif weighting is 2:
			title = "PSD (dB B)"
		else:
			title = "PSD (dB C)"
		
		ytitle = Qwt.QwtText(title)
		ytitle.setFont(QtGui.QFont(8))
		self.setAxisTitle(Qwt.QwtPlot.yLeft, ytitle)
	
	def drawCanvas(self, painter):
		t = QtCore.QTime()
		t.start()
		Qwt.QwtPlot.drawCanvas(self, painter)
		self.paint_time = (95.*self.paint_time + 5.*t.elapsed())/100.
