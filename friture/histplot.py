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

import PyQt4.Qwt5 as Qwt
from PyQt4 import QtCore, Qt, QtGui
from numpy import zeros, ones, log10, linspace, logspace, log2, array
#from log2_scale_engine import QwtLog10ScaleEngine
#import log2scale

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
		
		self.cached_bar_width = 1
		self.canvas_height = 2
		self.canvas_width = 2
		self.need_transform = False
		self.fl = [0.]
		self.fh = [0.]
		self.y = array([0.])
		self.y0 = 0.
		self.i = [0]
  		self.transform_slope = 1.
		self.transform_origin = 0.
		
		self.pixmaps = [QtGui.QPixmap()]
  
		self.yMap = None

	def setData(self, fl, fh, y):
		if len(self.y) <> len(y):
			self.fl = fl
			self.fh = fh
			self.need_transform = True
		
		self.y = array(y)
		
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
			result = Qwt.QwtDoubleRect(result.y(), result.x(), result.height(), result.width())
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
		# update the cache according to possibly new canvas dimensions
		h = rect.height()
		if h <> self.canvas_height:
			self.canvas_height = h
			self.need_transform = True
		w = rect.width()
		if w < self.canvas_width - 1 or w > self.canvas_width + 1:
			self.canvas_width = w
			self.need_transform = True

		# the transform parameters change when the scale changes
		if self.yMap <> yMap:
			self.yMap = yMap
			self.need_transform = True
		
		# update the cached pixmaps and coordinates if necessary
		if self.need_transform:
			self.x1 = [xMap.transform(flow) for flow in self.fl]
			self.x2 = [xMap.transform(fhigh)-1 for fhigh in self.fh]
			self.y0 = yMap.transform(self.baseline())
			
			self.update_pixmap(self.x2[0] - self.x1[0], self.canvas_height)
			self.i = list(array(self.x2) - array(self.x1) - (self.cached_bar_width - 2))   

			# [p1,p2] = [bottom pixel index, top pixel index]
			# [s1,s2] = [bottom value, top value]
   			if yMap.s2() - yMap.s1() <> 0.:
                                      self.transform_slope = (yMap.p1() - yMap.p2())/(yMap.s1() - yMap.s2())
                                      self.transform_origin = - yMap.s2() * (yMap.p1() - yMap.p2())/(yMap.s1() - yMap.s2()) + yMap.p2()                                      
			
			self.need_transform = False

		y = self.transform_slope * self.y + self.transform_origin
  
		for x1, x2, y2, i in zip(self.x1, self.x2, y, self.i):
			self.drawBar(painter, x1, y2, i)

	def drawBar(self, painter, left, top, i):
		painter.drawPixmap(left, top, self.pixmaps[i])

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
	def update_pixmap(self, width, height):
		self.cached_bar_width = width
		
		color = QtGui.QColor(self.color())
		
		self.pixmaps = []
		for w in range(width-2, width+3):
			pixmap = QtGui.QPixmap(w+1, height+1)
			pixmap.fill(color)
			painter = QtGui.QPainter(pixmap)
			if width > 3:
				self.drawBarDecoration(painter, w, height)
			self.pixmaps += [pixmap]
		
	def drawBarDecoration(self, painter, width, height):
		color = QtGui.QColor(self.color())
		factor = 125
		light = color.lighter(factor)
		dark = color.darker(factor)
		
		painter.setBrush(Qt.Qt.NoBrush)

		top = 0
		bottom = height
		left = 0
		right = width - 1

		#horizontal line
		painter.setPen(Qt.QPen(light, 2))
		painter.drawLine(1, top+2, right+1, top+2)

		#horizontal line
		painter.setPen(Qt.QPen(dark, 2))
		painter.drawLine(1, bottom, right+1, bottom)

		#vertical line
		painter.setPen(Qt.QPen(light, 1))
		painter.drawLine(0, top + 1, 0, bottom)
		painter.drawLine(1, top + 2, 1, bottom-1)
		
		#vertical line
		painter.setPen(Qt.QPen(dark, 1))
		painter.drawLine(right+1, top+1, right+1, bottom)
		painter.drawLine(right, top+2, right, bottom-1)

class HistogramPeakBarItem(Qwt.QwtPlotItem):
	def __init__(self, *args):
		Qwt.QwtPlotItem.__init__(self, *args)
		self.fl = [0.]
		self.fh = [0.]
		self.peaks = array([0.])
		self.palette_index = [0]
		#self.canvas_height = 2
		self.canvas_width = 2
		self.need_transform = False
		self.transform_slope = 1.
		self.transform_origin = 0.
		self.yMap = None
		
		self.palette = [Qt.QColor(255, gb, gb) for gb in range(0,256)]

	def setData(self, fl, fh, peaks, peaks_int):
		if len(self.peaks) <> len(peaks):
			self.fl = fl
			self.fh = fh
			self.need_transform = True
		
		self.peaks = peaks
		self.palette_index = (255*(1.-peaks_int)).astype(int)

	def draw(self, painter, xMap, yMap, rect):
		# update the cache according to possibly new canvas dimensions
		h = rect.height()
		w = rect.width()
		if w <> self.canvas_width:
			self.canvas_width = w
			self.need_transform = True

		# the transform parameters change when the scale changes
		if self.yMap <> yMap:
			self.yMap = yMap
			self.need_transform = True
		
		if self.need_transform:
			self.x1 = [xMap.transform(flow)+1 for flow in self.fl]
			self.x2 = [xMap.transform(fhigh)-1 for fhigh in self.fh]
   
			# [p1,p2] = [bottom pixel index, top pixel index]
			# [s1,s2] = [bottom value, top value]
   			if yMap.s2() - yMap.s1() <> 0.:
                                      self.transform_slope = (yMap.p1() - yMap.p2())/(yMap.s1() - yMap.s2())
                                      self.transform_origin = - yMap.s2() * (yMap.p1() - yMap.p2())/(yMap.s1() - yMap.s2()) + yMap.p2()                                      
			
			self.need_transform = False

		peaks = self.transform_slope * self.peaks + self.transform_origin
  
		for x1, x2, peak, index in zip(self.x1, self.x2, peaks, self.palette_index):
			painter.fillRect(x1-1, peak, x2-x1+2, h, self.palette[index])


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
		grid.enableXMin(True)
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
		
		# insert an additional plot item for the peak bar
		self.bar_peak = HistogramPeakBarItem()
		self.bar_peak.attach(self)
		self.peak = zeros((1,))
		self.peak_int = 0
		self.peak_decay = PEAK_DECAY_RATE
		
		self.histogram = HistogramItem()
		self.histogram.setColor(Qt.Qt.darkGreen)
		self.histogram.setBaseline(-200.)
		
		pos = [0.1, 1., 10.]
		self.histogram.setData(pos[:-1], pos[1:], pos[:-1])
		self.histogram.attach(self)
		
		self.cached_canvas = self.canvas()
		
		# set the size policy to "Preferred" to allow the widget to be shrinked under the default size, which is quite big
		self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
		
		#need to replot here for the size Hints to be computed correctly (depending on axis scales...)
		self.replot()

	def setdata(self, fl, fh, y):
		self.histogram.setData(fl, fh, y)
		
		self.compute_peaks(y)
		self.bar_peak.setData(fl, fh, self.peak, self.peak_int)
		
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
			self.peak_int = zeros(y.shape)
			self.peak_decay = y_ones * 20. * log10(PEAK_DECAY_RATE) * 5000

		mask1 = (self.peak < y)
		mask2 = (-mask1)
		mask2_a = mask2 * (self.peak_int < 0.2)
		mask2_b = mask2 * (self.peak_int >= 0.2)

		self.peak[mask1] = y[mask1]
		self.peak[mask2_a] = self.peak[mask2_a] + self.peak_decay[mask2_a]
		
		self.peak_decay[mask1] = 20. * log10(PEAK_DECAY_RATE) * 5000
		self.peak_decay[mask2_a] += 20. * log10(PEAK_DECAY_RATE) * 5000
		
		self.peak_int[mask1] = 1.
		self.peak_int[mask2_b] *= 0.975
	
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
