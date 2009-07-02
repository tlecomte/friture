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

from numpy import linspace, sin
from PyQt4 import Qt, QtGui
import PyQt4.Qwt5 as Qwt
	
class ClassPlot(Qwt.QwtPlot):

	def __init__(self, *args):
		Qwt.QwtPlot.__init__(self, *args)

		# set plot layout
		self.plotLayout().setMargin(0)
		self.plotLayout().setCanvasMargin(0)
		self.plotLayout().setAlignCanvasToScales(True)

		self.setAxisScale(Qwt.QwtPlot.yLeft, -1., 1.)

		# insert a few curves
		self.curve = Qwt.QwtPlotCurve()
		self.curve.setPen(QtGui.QPen(Qt.Qt.red))
		self.curve.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
		self.curve.attach(self)
		

		# temporarly initialize some data
		x = linspace(0.0, 10.0, 11)
		self.curve.setData(x, sin(x))

		# picker used to display coordinates in the status bar when clicking on the canvas
		self.picker = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom,
                               Qwt.QwtPlot.yLeft,
                               Qwt.QwtPicker.PointSelection,
                               Qwt.QwtPlotPicker.CrossRubberBand,
                               Qwt.QwtPicker.AlwaysOff,
                               self.canvas())

	def setdata(self,x,y):
		# we don't need so many points
		while len(y) > 2*self.canvas().width():
			x = (x[:-1:2] + x[1::2])/2.
			y = (y[:-1:2] + y[1::2])/2.
		self.curve.setData(x,y)
