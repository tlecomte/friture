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
from PyQt4 import QtCore

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
		
		self.connect(self.picker, QtCore.SIGNAL('moved(const QPoint &)'), self.moved)

	def moved(self, point):
		info = "Frequency=%d Hz, PSD=%d dB" % (
			self.invTransform(Qwt.QwtPlot.xBottom, point.x()),
			self.invTransform(Qwt.QwtPlot.yLeft, point.y()))
		self.emit(QtCore.SIGNAL("pointerMoved"), info)

	def setdata(self,x,y):
		if self.xmax <> x.max():
			print "changing x scale"
			self.xmax = x.max()
			if self.logfreqscale:
				self.setlogfreqscale()
			else:
				self.setlinfreqscale()
			self.needfullreplot = True

		classplot.ClassPlot.setdata(self,x,y)

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
		self.setAxisScale(Qwt.QwtPlot.xBottom, 0., self.xmax)
		self.needfullreplot = True

	def setlogfreqscale(self):
		self.logfreqscale = True
		self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLog10ScaleEngine())
		self.setAxisScale(Qwt.QwtPlot.xBottom, 20., self.xmax)
		self.needfullreplot = True
