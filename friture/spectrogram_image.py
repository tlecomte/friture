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

import numpy
from PyQt4 import Qt, QtCore, QtGui
import PyQt4.Qwt5 as Qwt

class CanvasScaledSpectrogram(QtCore.QObject):
	def __init__(self, logger, spectrum_length = 129, T = 10., canvas_height = 2,  canvas_width = 2):
		QtCore.QObject.__init__(self)
		
		# store the logger instance
		self.logger = logger
		
		self.spectrum_length = spectrum_length
		self.T = T
		self.canvas_height = canvas_height
		self.canvas_width = canvas_width
		self.logfreqscale = 0 # linear
		self.current_total = 0
		self.minfreq = 20.
		self.maxfreq = 20000.
		self.update_xscale()
		#self.fullspectrogram = numpy.zeros((self.canvas_height, self.time_bin_number(), 4), dtype = numpy.uint8)
		self.pixmap = QtGui.QPixmap(2*self.canvas_width,  self.canvas_height)
		#print "pixmap info : hasAlpha =", self.pixmap.hasAlpha(), ", depth =", self.pixmap.depth(), ", default depth =", self.pixmap.defaultDepth()
		self.pixmap.fill(QtGui.QColor("black"))
		self.painter = QtGui.QPainter()
		self.offset = 0
		# prepare a custom colormap black->blue->green->yellow->red->white
		self.colorMap = Qwt.QwtLinearColorMap(Qt.Qt.black, Qt.Qt.white)
		self.colorMap.addColorStop(0.2, Qt.Qt.blue)
		self.colorMap.addColorStop(0.4, Qt.Qt.green)
		self.colorMap.addColorStop(0.6, Qt.Qt.yellow)
		self.colorMap.addColorStop(0.8, Qt.Qt.red)
		self.prepare_palette()
		# performance timer
		self.time = QtCore.QTime()
		self.time.start()
		#self.logfile = open("latency_log.txt",'w')

	def erase(self):
		#self.fullspectrogram = numpy.zeros((self.canvas_height, self.time_bin_number(), 4), dtype = numpy.uint8)
		self.pixmap = QtGui.QPixmap(2*self.canvas_width,  self.canvas_height)
		self.pixmap.fill(QtGui.QColor("black"))
		self.offset = 0

	def time_bin_number(self):
		sampling_rate = 44100.
		Dt = 2*2.*(self.spectrum_length-1)/sampling_rate
		return self.T/Dt
		
	def n(self):
		return float(self.time_bin_number())/self.canvas_width

	def setT(self, T):
		if self.T <> T:
			self.T = T
			self.current_total = 0
			self.erase()
			self.logger.push("Spectrogram image: T changed, now: %.02f (%.03f frames per line)" %(T, self.n()))

	def setspectrum_length(self, spectrum_length):
		if self.spectrum_length <> spectrum_length:
			self.spectrum_length = spectrum_length
			self.current_total = 0
			self.erase()
			self.logger.push("Spectrogram image: spectrum_length changed, now: %d (%.03f frames per line)" %(spectrum_length, self.n()))

	def setcanvas_height(self, canvas_height):
		if self.canvas_height <> canvas_height:
			self.canvas_height = canvas_height
			self.update_xscale()
			self.erase()
			self.logger.push("Spectrogram image: canvas_height changed, now: %d (%.03f frames per line)" %(canvas_height, self.n()))

	def setcanvas_width(self, canvas_width):
		if self.canvas_width <> canvas_width:
			self.canvas_width = canvas_width
			self.current_total = 0
			self.erase()
			self.emit(QtCore.SIGNAL("canvasWidthChanged"), canvas_width)
			self.logger.push("Spectrogram image: canvas_width changed, now: %d (%.03f frames per line)" %(canvas_width, self.n()))

	def setlogfreqscale(self, logfreqscale):
		if logfreqscale <> self.logfreqscale:
			self.logger.push("Spectrogram image: freq scale changed %d" %(logfreqscale))
			self.logfreqscale = logfreqscale
			self.update_xscale()
			self.erase()

	def setfreqrange(self, minfreq, maxfreq):
		self.logger.push("Spectrogram image: freq range changed %.2f %.2f" %(minfreq, maxfreq))
		self.minfreq = minfreq
		self.maxfreq = maxfreq
		self.update_xscale()
		self.erase()

	def update_xscale(self):
		if self.logfreqscale == 2:
			self.xscaled = numpy.logspace(numpy.log2(self.minfreq), numpy.log2(self.maxfreq), self.canvas_height, base=2.0)
		elif self.logfreqscale == 1:
			self.xscaled = numpy.logspace(numpy.log10(self.minfreq), numpy.log10(self.maxfreq), self.canvas_height)
		else:
			self.xscaled = numpy.linspace(self.minfreq, self.maxfreq, self.canvas_height)

	def addData(self, freq, xyzs):
		spectrum_length = xyzs.shape[0]

		self.setspectrum_length(spectrum_length)

		# FIXME interpolation is only appropriate when the FFT frequency hop is larger
		# than the display frequency hop.
		# When the opposite is true, frequency bins should be summed up inside the display
		# frequency hop.
		# Use digitize or something to find what display bin a fft bin belongs to.
		#upsampling = 10.
		#upsampled_freq = numpy.linspace(freq.min(), freq.max(), len(freq)*upsampling)
		#upsampled_xyzs = xyzs.repeat(upsampling)
		#xyzs_buffer = numpy.histogram(upsampled_freq, bins=self.xscaled, normed=False, weights=upsampled_xyzs, new=None)[0]
		#xyzs_buffer /= upsampling
		
		xyzs_buffer = numpy.interp(self.xscaled, freq, xyzs)

		# draw !
		byteString = self.floats_to_bytes(xyzs_buffer[::-1])

		myimage = self.prepare_image(byteString, xyzs_buffer.shape[0])

		self.offset = (self.offset + 1) % self.canvas_width
		
		self.painter.begin(self.pixmap)
		self.painter.drawImage(self.offset, 0, myimage)
		self.painter.drawImage(self.offset + self.canvas_width, 0, myimage)
		self.painter.end()
		
		# reinitialize current_total
		self.current_total = 0.
		
		#self.logfile.write("%d\n"%self.time.restart())

	def floats_to_bytes(self, data):
		#dat1 = (255. * data).astype(numpy.uint8)
		#dat4 = dat1.repeat(4)
		dat4 = self.color_from_float(data).astype(numpy.uint32)
		return dat4.tostring()

	def prepare_image(self, byteString, length):
		myimage = QtGui.QImage(byteString, 1, length, QtGui.QImage.Format_RGB32)
		return myimage

	def prepare_palette(self):
		self.colors = numpy.zeros((256))
		for i in range(0, 256):
			self.colors[i] = self.colorMap.rgb(Qwt.QwtDoubleInterval(0,255), i)

	def color_from_float(self, v):
		d = (v*255).astype(numpy.uint8)
		return self.colors[d]

	#def interpolate_colors(colors, flat=False, num_colors=256):
		#colors = 
		#""" given a list of colors, create a larger list of colors interpolating
		#the first one. If flatten is True a list of numers will be returned. If
		#False, a list of (r,g,b) tuples. num_colors is the number of colors wanted
		#in the final list """
		
		#palette = []
		
		#for i in range(num_colors):
			#index = (i * (len(colors) - 1))/(num_colors - 1.0)
			#index_int = int(index)
			#alpha = index - float(index_int)
		
			#if alpha > 0:
			#r = (1.0 - alpha) * colors[index_int][0] + alpha * colors[index_int + 1][0]
			#g = (1.0 - alpha) * colors[index_int][1] + alpha * colors[index_int + 1][1]
			#b = (1.0 - alpha) * colors[index_int][2] + alpha * colors[index_int + 1][2]
			#else:
			#r = (1.0 - alpha) * colors[index_int][0]
			#g = (1.0 - alpha) * colors[index_int][1]
			#b = (1.0 - alpha) * colors[index_int][2]
		
			#if flat:
			#palette.extend((int(r), int(g), int(b)))
			#else:
			#palette.append((int(r), int(g), int(b)))
		
		#return palette

	def getpixmap(self):
		return self.pixmap

	def getpixmapoffset(self):
		return self.offset + 1

# plan :
# 1. quickly convert each piece of data to a pixmap, with the right pixel size
# as QImage to QPixmap conversion is slow, and scaling is slow too
# 2. use a cache of size M=2*N
# 3. write in the cache at the position j and j+N
# 4. the data part that is to be drawn can be read contiguously from j+1 to j+1+N
