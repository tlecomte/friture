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

import classplot
import PyQt4.Qwt5 as Qwt
from PyQt4 import QtCore, Qt, QtGui
from numpy import zeros, ones, log10
from log2_scale_engine import QwtLog10ScaleEngine

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

class SpectPlot(classplot.ClassPlot):
	def __init__(self, *args):
		classplot.ClassPlot.__init__(self, *args)

		# we do not need caching
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintCached, False)
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintPacked, False)

		self.setAxisScale(Qwt.QwtPlot.yLeft, -140., 0.)
		self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Frequency (Hz)')
		self.setAxisTitle(Qwt.QwtPlot.yLeft, 'PSD (dB)')
		#self.axisWidget(Qwt.QwtPlot.xBottom).setFont(self.font())

		self.xmax = 0
		self.needfullreplot = False

		self.setlinfreqscale()
		self.logfreqscale = False
		
		self.setfreqrange(20., 20000.)
		
		self.setAxisScaleDraw(Qwt.QwtPlot.xBottom, FreqScaleDraw())
		
		self.connect(self.picker, QtCore.SIGNAL('moved(const QPoint &)'), self.moved)
		
		# insert an additional curve for the peak
		self.curve_peak = Qwt.QwtPlotCurve()
		self.curve_peak.setPen(QtGui.QPen(Qt.Qt.blue))
		self.curve_peak.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
		self.curve_peak.attach(self)
		self.peak = zeros((1,))
		self.peakHold = 0
		self.peakDecay = PEAK_DECAY_RATE
	
	def moved(self, point):
		info = "Frequency=%d Hz, PSD=%d dB" % (
			self.invTransform(Qwt.QwtPlot.xBottom, point.x()),
			self.invTransform(Qwt.QwtPlot.yLeft, point.y()))
		self.emit(QtCore.SIGNAL("pointerMoved"), info)

	def setdata(self,x,y):
		if self.xmax <> x.max():
			print "changing x scale"
			self.xmax = x.max()
			self.needfullreplot = True

		if len(self.peak) <> len(y):
			self.ones = ones(y.shape)
			self.peak = self.ones*(-500.)
			self.peakHold = zeros(y.shape)
			self.peakDecay = self.ones * PEAK_DECAY_RATE

		dBdecay = 20.*log10(self.peakDecay)

		mask1 = (self.peak < y)
		mask2 = (-mask1) * (self.peakHold > self.ones*(PEAK_FALLOFF_COUNT - 1.))
		mask2_bis = mask2 * (self.peak + dBdecay < y)
		mask2_ter = mask2 * (self.peak + dBdecay >= y)
		mask3 = (-mask1) * (-mask2)

		self.peak = mask1 * y \
		+ mask2_bis * y \
		+ mask2_ter * (self.peak + dBdecay) \
		+ mask3 * self.peak
		
		self.peakDecay = mask1 * self.ones * PEAK_DECAY_RATE \
		+ mask2_bis * self.peakDecay \
		+ mask2_ter * (self.peakDecay ** 2) \
		+ mask3 * self.peakDecay
		
		self.peakHold = (-mask1) * self.peakHold
		self.peakHold += self.ones
		
		classplot.ClassPlot.setdata(self,x,y)
		self.curve_peak.setData(x, self.peak)
		
		if self.needfullreplot:
			self.needfullreplot = False
			self.replot()
		else:
			# self.replot() would call updateAxes() which is dead slow (probably because it
			# computes label sizes); instead, let's just ask Qt to repaint the canvas next time
			# This works because we disable the cache
			self.canvas().update()

	def setlinfreqscale(self):
		self.logfreqscale = False
		self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLinearScaleEngine())
		self.needfullreplot = True

	def setlogfreqscale(self):
		self.logfreqscale = True
		self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLog10ScaleEngine())
		self.needfullreplot = True

	def setfreqrange(self, minfreq, maxfreq):
		self.minfreq = minfreq
		self.maxfreq = maxfreq
		self.setAxisScale(Qwt.QwtPlot.xBottom, self.minfreq, self.maxfreq)
		self.needfullreplot = True
