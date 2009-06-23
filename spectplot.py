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

		self.setlinfreqscale()

		self.xmax = 0

	def setdata(self,x,y):
		needfullreplot = False
		if self.xmax <> x.max():
			print "changing x scale"
			self.xmax = x.max()
			self.setAxisScale(Qwt.QwtPlot.xBottom, 0., self.xmax)
			needfullreplot = True

		classplot.ClassPlot.setdata(self,x,y)

		if needfullreplot:
			self.replot()
		else:
			# self.replot() would call updateAxes() which is dead slow (probably because it
			# computes label sizes); instead, let's just ask Qt to repaint the canvas next time
			# This works because we disable the cache
			self.canvas().update()

	def setlinfreqscale(self):
		self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLinearScaleEngine())

	def setlogfreqscale(self):
		self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLog10ScaleEngine())