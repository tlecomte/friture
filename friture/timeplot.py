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
from numpy import log10, interp, linspace

class picker(Qwt.QwtPlotPicker):
	def __init__(self, *args):
		Qwt.QwtPlotPicker.__init__(self, *args)
		
	def trackerText(self, pos):
		pos2 = self.invTransform(pos)
		return Qwt.QwtText("%.3g ms, %.3g" %(pos2.x(), pos2.y()))

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

class TimePlot(ClassPlot):
	def __init__(self, parent, logger):
		ClassPlot.__init__(self)

		# store the logger instance
		self.logger = logger

		# we do not need caching
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintCached, False)
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintPacked, False)

		# attach a grid
		grid = Qwt.QwtPlotGrid()
		grid.setMajPen(Qt.QPen(Qt.Qt.lightGray))
		grid.attach(self)

		xtitle = Qwt.QwtText('Time (ms)')
		xtitle.setFont(QtGui.QFont(8))
		self.setAxisTitle(Qwt.QwtPlot.xBottom, xtitle)
		self.setAxisScale(Qwt.QwtPlot.yLeft, -1., 1.)
		# self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Time (ms)')
		self.xmin = 0.
		self.xmax = 1.

		ytitle = Qwt.QwtText('Signal')
		ytitle.setFont(QtGui.QFont(8))
		self.setAxisTitle(Qwt.QwtPlot.yLeft, ytitle)
		# self.setAxisTitle(Qwt.QwtPlot.yLeft, 'Signal')
		self.setAxisScale(Qwt.QwtPlot.yLeft, -1., 1.)
		self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLinearScaleEngine())
		
		self.paint_time = 0.
		
		self.canvas_width = 0
  
		self.dual_channel = False
  
  		# insert an additional curve for the second channel
  		# (ClassPlot already has one by default)
		self.curve2 = Qwt.QwtPlotCurve("Ch2")
		self.curve2.setPen(QtGui.QPen(Qt.Qt.blue))
		#self.curve.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
		#self.curve2.attach(self)

  		# gives an appropriate title to the first curve
  		# (for the legend)
		self.curve.setTitle("Ch1")
		
		# picker used to display coordinates when clicking on the canvas
		self.picker = picker(Qwt.QwtPlot.xBottom,
                               Qwt.QwtPlot.yLeft,
                               Qwt.QwtPicker.PointSelection,
                               Qwt.QwtPlotPicker.CrossRubberBand,
                               Qwt.QwtPicker.ActiveOnly,
                               self.canvas())
		
		self.cached_canvas = self.canvas()
		
		#need to replot here for the size Hints to be computed correctly (depending on axis scales...)
		self.replot()

	def setdata(self, x, y):
		if self.canvas_width <> self.cached_canvas.width():
			self.logger.push("timeplot : changed canvas width")
			self.canvas_width = self.cached_canvas.width()
			self.update_xscale()

		if self.dual_channel:
			self.dual_channel = False
			self.curve2.detach()
  			# disable the legend
  			# (useless when one channel is active)
			self.insertLegend(None, Qwt.QwtPlot.RightLegend)

		x_ms =  1e3*x
		needfullreplot = False
		if self.xmax <> x_ms[-1]:
			self.logger.push("timeplot : changing x max")
			self.xmax = x_ms[-1]
			self.setAxisScale(Qwt.QwtPlot.xBottom, self.xmin, self.xmax)
			self.update_xscale()
			needfullreplot = True
		if self.xmin <> x_ms[0]:
			self.logger.push("timeplot : changing x min")
			self.xmin = x_ms[0]
			self.setAxisScale(Qwt.QwtPlot.xBottom, self.xmin, self.xmax)
			self.update_xscale()
			needfullreplot = True

		y_interp = interp(self.xscaled, x_ms, y)
		ClassPlot.setdata(self, self.xscaled, y_interp)

		if needfullreplot:
			self.replot()
		else:
			# self.replot() would call updateAxes() which is dead slow (probably because it
			# computes label sizes); instead, let's just ask Qt to repaint the canvas next time
			# This works because we disable the cache
			self.cached_canvas.update()

	def setdataTwoChannels(self, x, y, y2):
		if self.canvas_width <> self.cached_canvas.width():
			self.logger.push("timeplot : changed canvas width")
			self.canvas_width = self.cached_canvas.width()
			self.update_xscale()

		if not self.dual_channel:
			self.dual_channel = True
			self.curve2.attach(self)
  			# enable the legend
  			# (to discrimate between the two channels)
			self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.RightLegend)
		
		x_ms =  1e3*x
		needfullreplot = False
		if self.xmax <> x_ms[-1]:
			self.logger.push("timeplot : changing x max")
			self.xmax = x_ms[-1]
			self.setAxisScale(Qwt.QwtPlot.xBottom, self.xmin, self.xmax)
			self.update_xscale()
			needfullreplot = True
		if self.xmin <> x_ms[0]:
			self.logger.push("timeplot : changing x min")
			self.xmin = x_ms[0]
			self.setAxisScale(Qwt.QwtPlot.xBottom, self.xmin, self.xmax)
			self.update_xscale()
			needfullreplot = True

		#y_interp = interp(self.xscaled, x_ms, y)
  		#y_interp2 = interp(self.xscaled, x_ms, y2)
		#ClassPlot.setdata(self, self.xscaled, y_interp)
		#self.curve2.setData(self.xscaled, y_interp2)
		ClassPlot.setdata(self, x_ms, y)
		self.curve2.setData(x_ms, y2)

		if needfullreplot:
			self.replot()
		else:
			# self.replot() would call updateAxes() which is dead slow (probably because it
			# computes label sizes); instead, let's just ask Qt to repaint the canvas next time
			# This works because we disable the cache
			self.cached_canvas.update()

	def update_xscale(self):
		self.xscaled = linspace(self.xmin, self.xmax, self.canvas_width)

	def drawCanvas(self, painter):
		t = QtCore.QTime()
		t.start()
		Qwt.QwtPlot.drawCanvas(self, painter)
		self.paint_time = (95.*self.paint_time + 5.*t.elapsed())/100.
