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

from friture.classplot import ClassPlot
import PyQt4.Qwt5 as Qwt
from PyQt4 import QtCore, Qt, QtGui
from numpy import zeros, ones, log10, linspace, logspace, interp, log2, histogram
#from log2_scale_engine import QwtLog10ScaleEngine

# The peak decay rates (magic goes here :).
PEAK_DECAY_RATE = 1.0 - 3E-6
# Number of cycles the peak stays on hold before fall-off.
PEAK_FALLOFF_COUNT = 32 # default : 16

class FreqScaleDraw(Qwt.QwtScaleDraw):
	def __init__(self, *args):
		Qwt.QwtScaleDraw.__init__(self, *args)

	def label(self, value):
		if value >= 1e3:
			label = "%gk" %(value/1e3)
		else:
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

class SpectPlot(ClassPlot):
	def __init__(self, parent, logger):
		ClassPlot.__init__(self)

		# store the logger instance
		self.logger = logger

		# we do not need caching
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintCached, False)
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintPacked, False)

		self.ymin = -140.
		self.setAxisScale(Qwt.QwtPlot.yLeft, self.ymin, 0.)
		self.baseline_transformed = False
		self.baseline = 0.
		self.curve.setBaseline(self.ymin)
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
		grid.setZ(1000.)
		grid.attach(self)

		self.xmax = 0
		self.needfullreplot = False

		self.canvas_width = 0
		self.logfreqscale = False
		self.setfreqrange(20., 20000.)
		self.setlinfreqscale()
		
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
		self.curve_peak = Qwt.QwtPlotCurve()
		#self.curve_peak.setPen(QtGui.QPen(Qt.Qt.blue))
		self.curve_peak.setPen(Qt.QColor("#FF9000")) #dark orange
		#self.curve_peak.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
		#self.curve_peak.setPen(QtGui.QPen(Qt.Qt.NoPen))
		#self.curve_peak.setBrush(Qt.Qt.blue)
		self.curve_peak.attach(self)
		self.peak = zeros((1,))
		self.peakHold = 0
		self.peakDecay = PEAK_DECAY_RATE
		self.peaks_enabled = True
		
		# fill under the curve
		#self.curve.setBrush(Qt.QColor(255,0,190))
		#self.curve.setBrush(Qt.Qt.red)
		self.curve.setBrush(Qt.QColor("#057D9F")) #some sort of blue
		#self.curve.setPen(Qt.QColor(255,0,0,0))
		#self.curve.setPen(QtGui.QPen(Qt.Qt.red))
		self.curve.setPen(QtGui.QPen(Qt.Qt.NoPen))
		#self.curve.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
		
		self.cached_canvas = self.canvas()
		
		#need to replot here for the size Hints to be computed correctly (depending on axis scales...)
		self.replot()

	def setdata(self, x, y):
		if self.canvas_width <> self.cached_canvas.width():
			self.logger.push("spectplot : changed canvas width")
			self.canvas_width = self.cached_canvas.width()
			self.update_xscale()
		
		if self.xmax <> x[-1]:
			self.logger.push("spectplot : changing x scale")
			self.xmax = x[-1]
			self.update_xscale()
			self.needfullreplot = True
		
		y_interp = interp(self.xscaled, x, y)
                
		#upsampling = 10.
		#upsampled_freq = linspace(x.min(), x.max(), len(x)*upsampling)
		#upsampled_xyzs = y.repeat(upsampling)
		#y_interp = histogram(upsampled_freq, bins=self.xscaled, normed=False, weights=upsampled_xyzs, new=None)[0]
		#y_interp /= upsampling
                
		ClassPlot.setdata(self, self.xscaled, y_interp)

		if self.peaks_enabled:
			self.compute_peaks(y_interp)
			self.curve_peak.setData(self.xscaled, self.peak)
		
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

	def update_xscale(self):
		#if self.logfreqscale == 2:
			#self.xscaled = logspace(log2(self.minfreq), log2(self.maxfreq), self.canvas_width, base=2.0)
		if self.logfreqscale:
			self.xscaled = logspace(log10(self.minfreq), log10(self.maxfreq), self.canvas_width)
		else:
			self.xscaled = linspace(self.minfreq, self.maxfreq, self.canvas_width)

	def setlinfreqscale(self):
		self.logfreqscale = False
		self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLinearScaleEngine())
		self.update_xscale()
		self.needfullreplot = True

	def setlogfreqscale(self):
		self.logfreqscale = True
		self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLog10ScaleEngine())
		self.update_xscale()
		self.needfullreplot = True

	def setfreqrange(self, minfreq, maxfreq):
		self.minfreq = minfreq
		self.maxfreq = maxfreq
		self.setAxisScale(Qwt.QwtPlot.xBottom, self.minfreq, self.maxfreq)
		self.update_xscale()
		self.needfullreplot = True
	
	def setspecrange(self, min, max):
		self.ymin = min
		self.setAxisScale(Qwt.QwtPlot.yLeft, min, max)
		if self.baseline_transformed:
			self.curve.setBaseline(self.baseline)
		else:
			# FIXME
			self.curve.setBaseline(min)
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

	def set_peaks_enabled(self, enabled):
		self.peaks_enabled = enabled

	def set_baseline_displayUnits(self, baseline):
		# FIXME
		self.baseline_transformed = False
		self.curve.setBaseline(self.ymin)

	def set_baseline_dataUnits(self, baseline):
		self.baseline_transformed = True
		self.curve.setBaseline(baseline)

	def drawCanvas(self, painter):
		t = QtCore.QTime()
		t.start()
		Qwt.QwtPlot.drawCanvas(self, painter)
		self.paint_time = (95.*self.paint_time + 5.*t.elapsed())/100.
