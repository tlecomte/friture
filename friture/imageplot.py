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

import PyQt4.Qwt5 as Qwt
from PyQt4 import QtCore, QtGui, Qt
from friture.spectrogram_image import CanvasScaledSpectrogram
from online_linear_2D_resampler import Online_Linear_2D_resampler
from fractions import Fraction
from frequency_resampler import Frequency_Resampler
import numpy as np

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
		return Qwt.QwtText("%.2f s, %d Hz" %(pos2.x(), pos2.y()))
			
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

class PlotImage(Qwt.QwtPlotItem):
	def __init__(self, logger, audiobackend):
		Qwt.QwtPlotItem.__init__(self)
		self.canvasscaledspectrogram = CanvasScaledSpectrogram(logger)
		self.T = 0.
		self.dT = 1.
		self.audiobackend = audiobackend
		#self.previous_time = self.audiobackend.get_stream_time()
		self.offset = 0 #self.audiobackend.get_stream_time()/self.dT
		
		self.jitter_s = 0.

		self.isPlaying = True

		self.sfft_rate_frac = Fraction(1, 1)
		self.frequency_resampler = Frequency_Resampler()
		self.resampler = Online_Linear_2D_resampler()

		self.timer = QtCore.QElapsedTimer()
		self.timer.start()

	def addData(self, freq, xyzs, logfreqscale):
		self.frequency_resampler.setlogfreqscale(logfreqscale)

		# Note: both the frequency and the time resampler work
		# only on 1D arrays, so we loop on the columns of data.
		# However, we reassemble the 2D output before drawing
		# on the widget's pixmap, because the drawing operation
		# seems to have a costly warmup phase, so it is better
		# to invoke it the fewer number of times possible.

		n = self.resampler.processable(xyzs.shape[1])
		resampled_data = np.zeros((self.frequency_resampler.nsamples, n))

		i = 0
		for j in range(xyzs.shape[1]):
			freq_resampled_data = self.frequency_resampler.process(freq, xyzs[:, j])
			data = self.resampler.process(freq_resampled_data)
			resampled_data[:,i:i+data.shape[1]] = data
			i += data.shape[1]

		self.canvasscaledspectrogram.addData(resampled_data)

	def pause(self):
		self.isPlaying = False

	def restart(self):
		self.isPlaying = True
		self.timer.restart()

	def draw(self, painter, xMap, yMap, rect):
		# update the spectrogram according to possibly new canvas dimensions
		self.frequency_resampler.setnsamples(rect.height())
		self.resampler.set_height(rect.height())
		self.canvasscaledspectrogram.setcanvas_height(rect.height())
		#print self.jitter_s, self.T, rect.width(), rect.width()*(1 + self.jitter_s/self.T)
		jitter_pix = rect.width()*self.jitter_s/self.T
		self.canvasscaledspectrogram.setcanvas_width(rect.width() + jitter_pix)

		screen_rate_frac = Fraction(rect.width(), int(self.T*1000))
		self.resampler.set_ratio(self.sfft_rate_frac, screen_rate_frac)

		# time advance
		# FIXME ideally this function should be called at paintevent time, for better time sync
		# but I'm not sure it is... maybe qwt does some sort of double-buffering
		# and repaints its items outside of paintevents
		# solution: look at PaintEvent

		# FIXME there is a small bands of columns with jitter (on both sides of the spectrogram)
		# solution: grow the rolling-canvas by a couple of columns,
		# and slightly delay the spectrogram by the same number of columns

		if self.isPlaying:
			delta_t = self.timer.nsecsElapsed()*1e-9
			self.timer.restart()
			pixel_advance = delta_t/(self.T + self.jitter_s)*rect.width()
			self.canvasscaledspectrogram.addPixelAdvance(pixel_advance)

		pixmap = self.canvasscaledspectrogram.getpixmap()
		offset = self.canvasscaledspectrogram.getpixmapoffset(delay=jitter_pix/2)
		
		rolling = True
		if rolling:
			# draw the whole canvas with a selected portion of the pixmap

			hints = painter.renderHints()
			# enable bilinear pixmap transformation
			painter.setRenderHints(hints|QtGui.QPainter.SmoothPixmapTransform)
			#FIXME instead of a generic bilinear transformation, I need a specialized one
			# since no transformation is needed in y, and the sampling rate is already known to be ok in x
			sw = rect.width()
			sh = rect.height()

			source_rect = QtCore.QRectF(offset, 0, sw, sh)
			# QRectF since the offset and width may be non-integer
			painter.drawPixmap(QtCore.QRectF(rect), pixmap, source_rect)
		else:
			sw = rect.width()
			sh = rect.height()
			source_rect = QtCore.QRectF(0, 0, sw, sh)
			painter.drawPixmap(QtCore.QRectF(rect), pixmap, source_rect)

	def settimerange(self, timerange_seconds, dT):
		self.T = timerange_seconds
		self.dT = dT

	def setfreqrange(self, minfreq, maxfreq):
		self.frequency_resampler.setfreqrange(minfreq, maxfreq)

	def set_sfft_rate(self, rate_frac):
		self.sfft_rate_frac = rate_frac

	def setlogfreqscale(self, logfreqscale):
		self.frequency_resampler.setlogfreqscale(logfreqscale)

	def erase(self):
		self.canvasscaledspectrogram.erase()

	def set_jitter(self, jitter_s):
		self.jitter_s = jitter_s
		#print jitter_s

class ImagePlot(Qwt.QwtPlot):

	def __init__(self, parent, logger, audiobackend):
		Qwt.QwtPlot.__init__(self, parent)

		# we do not need caching
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintCached, False)
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintPacked, False)
		# we do not need to have the background erased on each repaint
		self.canvas().setAttribute(Qt.Qt.WA_NoSystemBackground)

		# set plot layout
		self.plotLayout().setMargin(0)
		self.plotLayout().setCanvasMargin(0)
		self.plotLayout().setAlignCanvasToScales(True)
		# use custom labelling for frequencies
		self.setAxisScaleDraw(Qwt.QwtPlot.yLeft, FreqScaleDraw())
		# set axis titles
		xtitle = Qwt.QwtText('Time (s)')
		xtitle.setFont(QtGui.QFont(8))
		self.setAxisTitle(Qwt.QwtPlot.xBottom, xtitle)
		# self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Time (s)')
		ytitle = Qwt.QwtText('Frequency (Hz)')
		ytitle.setFont(QtGui.QFont(8))
		self.setAxisTitle(Qwt.QwtPlot.yLeft, ytitle)
		# self.setAxisTitle(Qwt.QwtPlot.yLeft, 'Frequency (Hz)')
		
		# attach a plot image
		self.plotImage = PlotImage(logger, audiobackend)
		self.plotImage.attach(self)
		self.setlinfreqscale()
		self.setfreqrange(20., 20000.)
		
		self.rightAxis = self.axisWidget(Qwt.QwtPlot.yRight)
		ctitle = Qwt.QwtText("PSD (dB A)")
		ctitle.setFont(QtGui.QFont(8))
		self.setAxisTitle(Qwt.QwtPlot.yRight, ctitle)
		self.rightAxis.setColorBarEnabled(True)
		self.enableAxis(Qwt.QwtPlot.yRight)
		self.setspecrange(-140., 0.)

		self.setAxisScale(Qwt.QwtPlot.xBottom, 0., 10.)
		
		self.paint_time = 0.
		
		# picker used to display coordinates when clicking on the canvas
		self.picker = picker(Qwt.QwtPlot.xBottom,
                               Qwt.QwtPlot.yLeft,
                               Qwt.QwtPicker.PointSelection,
                               Qwt.QwtPlotPicker.CrossRubberBand,
                               Qwt.QwtPicker.ActiveOnly,
                               self.canvas())
		
		self.cached_canvas = self.canvas()
		
		# set the size policy to "Preferred" to allow the widget to be shrinked under the default size, which is quite big
		self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
		
		#need to replot here for the size Hints to be computed correctly (depending on axis scales...)
		self.replot()

	def addData(self, freq, xyzs):
		self.plotImage.addData(freq, xyzs, self.logfreqscale)

	def updatePlot(self):
		# self.replot() would call updateAxes() which is dead slow (probably because it
		# computes label sizes); instead, let's ask Qt to repaint the canvas only next time
		# This works because we disable the cache
		# TODO what happens when the cache is enabled ?
		# Could that solve the perceived "unsmoothness" ?
		
		self.cached_canvas.update()
		
		#print self.canvas().testPaintAttribute(Qwt.QwtPlotCanvas.PaintCached)
		#print self.canvas().paintCache()

	def pause(self):
		self.plotImage.pause()

	def restart(self):
		self.plotImage.restart()

	def setlinfreqscale(self):
		self.plotImage.erase()
		self.logfreqscale = 0
		self.plotImage.setlogfreqscale(False)
		self.setAxisScaleEngine(Qwt.QwtPlot.yLeft, Qwt.QwtLinearScaleEngine())
		self.replot()

	def setlog10freqscale(self):
		self.plotImage.erase()
		self.logfreqscale = 1
		self.plotImage.setlogfreqscale(True)
		self.setAxisScaleEngine(Qwt.QwtPlot.yLeft, Qwt.QwtLog10ScaleEngine())
		self.replot()
		
	#def setlog2freqscale(self):
	#	self.plotImage.erase()
	#	self.logfreqscale = 2
	#	print "Warning: Frequency scales are not implemented in the spectrogram"
	#	self.setAxisScaleEngine(Qwt.QwtPlot.yLeft, Qwt.QwtLog10ScaleEngine())
	#	self.replot()

	def settimerange(self, timerange_seconds, dT_seconds):   
		self.plotImage.settimerange(timerange_seconds, dT_seconds)
		self.setAxisScale(Qwt.QwtPlot.xBottom, 0., timerange_seconds)
		self.replot()

	def set_sfft_rate(self, rate_frac):
		self.plotImage.set_sfft_rate(rate_frac)

	def setfreqrange(self, minfreq, maxfreq):
		self.plotImage.setfreqrange(minfreq, maxfreq)
		self.setAxisScale(Qwt.QwtPlot.yLeft, minfreq, maxfreq)
		self.replot()
	
	def setspecrange(self, spec_min, spec_max):
		self.rightAxis.setColorMap(Qwt.QwtDoubleInterval(spec_min, spec_max), self.plotImage.canvasscaledspectrogram.colorMap)
		self.setAxisScale(Qwt.QwtPlot.yRight, spec_min, spec_max)
		self.replot()
		
	def setweighting(self, weighting):
		if weighting is 0:
			title = "PSD (dB)"
		elif weighting is 1:
			title = "PSD (dB A)"
		elif weighting is 2:
			title = "PSD (dB B)"
		else:
			title = "PSD (dB C)"
		
		ctitle = Qwt.QwtText(title)
		ctitle.setFont(QtGui.QFont(8))
		self.setAxisTitle(Qwt.QwtPlot.yRight, ctitle)
	
	def drawCanvas(self, painter):
		t = QtCore.QTime()
		t.start()
		Qwt.QwtPlot.drawCanvas(self, painter)
		self.paint_time = (95.*self.paint_time + 5.*t.elapsed())/100.
