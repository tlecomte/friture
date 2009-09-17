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
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt

class AudioData():
	def __init__ (self, rawdata, nchannels, format, samplesize, samplerate):
		self.rawdata = rawdata
		self.floatdata = numpy.fromstring(self.rawdata,numpy.int32)/2.**31
		self.nchannels = nchannels
		self.format = format
		self.samplesize = samplesize
		self.samplerate = samplerate
		self.nframes = len(self.floatdata)

def concatenate(data1, data2):
    if data1 == None:
        return data2
    if data2 == None:
        return data1
    return AudioData(data1.rawdata + data2.rawdata, data1.nchannels, data1.format, data1.samplesize, data1.samplerate)

#class RawSpectrogram():
	#def __init__(self, vsize = 0, hsize = 129):
		#self.vsize = vsize
		#self.hsize = hsize
		#if self.vsize == 0:
			#self.vsize = 2**18/((self.hsize-1)*2)
		#self.fullspectrogram = numpy.zeros((self.hsize, self.vsize))
	#def erase(self):
		#self.fullspectrogram = numpy.zeros((self.hsize, self.vsize))
	#def sethsize(self,hsize):
		#if self.hsize <> hsize:
			#self.hsize = hsize
			#self.erase()
	#def addData(self, xyzs):
		#if xyzs.ndim == 1:
			#hsize = xyzs.shape[0]
			#vsize = 1
		#else:
			#hsize = xyzs.shape[0]
			#vsize = xyzs.shape[1]

		#if hsize<>self.hsize:
			#self.sethsize(hsize)

		#self.fullspectrogram = numpy.hstack((self.fullspectrogram[vsize:,:],xyzs))

	#def data(self):
		#return self.fullspectrogram

#class FreqScaledSpectrogram():
	#def __init__(self, vsize = 0, hsize = 129):
		#self.hsize = hsize
		#self.vsize = vsize
		#if self.vsize == 0:
			#self.vsize = 2**18/((self.hsize-1)*2)
		#self.fullspectrogram = numpy.zeros((self.hsize, self.vsize))

	#def erase(self):
		#self.fullspectrogram = numpy.zeros((self.hsize, self.vsize))

	#def sethsize(self,hsize):
		#if self.hsize <> hsize:
			#self.hsize = hsize
			#self.erase()

	#def addData(self, xyzs, logfreqscale = 0):
		#if xyzs.ndim == 1:
			#hsize = xyzs.shape[0]
			#vsize = 1
		#else:
			#hsize = xyzs.shape[0]
			#vsize = xyzs.shape[1]

		#if hsize<>self.hsize:
			#self.sethsize(hsize)

		#if logfreqscale == 0:
			#freqscaled_xyzs = xyzs #NOP
		#else:
			## ideally, we should directly interpolate to the canvas vsize
			#x = numpy.arange(0, hsize)*22050./hsize
			#xlog = numpy.logspace(numpy.log10(20),numpy.log10(22050),hsize)

		#if hsize == 1:
			#freqscaled_xyzs = numpy.interp(xlog,x,xyzs)
		#else:
			#freqscaled_xyzs = numpy.interp(xlog,x,xyzs[0,:])

		#for i in range(1,vsize):
		    #freqscaled_xyzs = numpy.hstack((freqscaled_xyzs,numpy.interp(xlog,x,xyzs[i,:])))

		#self.fullspectrogram = numpy.hstack((self.fullspectrogram[vsize:,:],freqscaled_xyzs))

	#def data(self):
		#return self.fullspectrogram

class CanvasScaledSpectrogram():
	def __init__(self, vsize = 129, hsize = 0, canvas_vsize = 2,  canvas_hsize = 2):
		self.hsize = hsize
		self.vsize = vsize
		self.logfreqscale = False
		if self.hsize == 0:
			T = 10.
			sampling_rate = 44100.
			Dt = 2*2.*(self.vsize-1)/sampling_rate
			self.hsize = T/Dt
		self.canvas_vsize = canvas_vsize
		self.canvas_hsize = canvas_hsize
		self.n = float(self.hsize)/canvas_hsize
		self.current_total = 0
		self.x = numpy.linspace(0., 22050., vsize)
		self.update_xscale()
		self.fullspectrogram = numpy.zeros((self.canvas_vsize, self.hsize, 4), dtype = numpy.uint8)
		self.xyzs_buffer = numpy.zeros((self.canvas_vsize))
		self.pixmap = Qt.QPixmap(2*self.canvas_hsize,  self.canvas_vsize)
		self.pixmap.fill(Qt.QColor("black"))
		self.painter = Qt.QPainter(self.pixmap)
		#self.spectrogramstr = ['\0']*self.canvas_vsize*self.vsize*4
		self.offset = 0
		# prepare a custom colormap black->blue->green->yellow->red->white
		self.colorMap = Qwt.QwtLinearColorMap(Qt.Qt.black, Qt.Qt.white)
		self.colorMap.addColorStop(0.2, Qt.Qt.blue)
		self.colorMap.addColorStop(0.4, Qt.Qt.green)
		self.colorMap.addColorStop(0.6, Qt.Qt.yellow)
		self.colorMap.addColorStop(0.8, Qt.Qt.red)
		self.prepare_palette()

	def erase(self):
		self.fullspectrogram = numpy.zeros((self.canvas_vsize, self.hsize, 4), dtype = numpy.uint8)
		self.xyzs_buffer = numpy.zeros((self.canvas_vsize))
		del self.painter
		del self.pixmap
		self.pixmap = Qt.QPixmap(2*self.canvas_hsize,  self.canvas_vsize)
		self.pixmap.fill(Qt.QColor("black"))
		self.painter = Qt.QPainter(self.pixmap)
		#self.spectrogramstr = ['\0']*self.canvas_vsize*self.vsize*4
		self.offset = 0

	def setvsize(self, vsize):
		if self.vsize <> vsize:
			print "vsize changed", vsize
			self.vsize = vsize
			
			T = 10.
			sampling_rate = 44100.
			Dt = 2*2.*(self.vsize-1)/sampling_rate
			self.hsize = T/Dt
			self.n = float(self.hsize)/self.canvas_hsize
			self.current_total = 0

			self.erase()
			self.x = numpy.linspace(0., 22050., vsize)

	def setcanvas_vsize(self, canvas_vsize):
		if self.canvas_vsize <> canvas_vsize:
			print "canvas_vsize changed",  canvas_vsize
			self.canvas_vsize = canvas_vsize
			self.update_xscale()
			self.erase()

	def setcanvas_hsize(self, canvas_hsize):
		if self.canvas_hsize <> canvas_hsize:
			self.canvas_hsize = canvas_hsize
			self.n = float(self.hsize)/canvas_hsize
			self.current_total = 0
			self.erase()
			print "canvas_hsize changed",  canvas_hsize,  self.n

	def update_xscale(self):
		if self.logfreqscale == False:
			self.xscaled = numpy.linspace(0., 22050., self.canvas_vsize)
		else:
			self.xscaled = numpy.logspace(numpy.log10(20.), numpy.log10(22050.), self.canvas_vsize)

	def setlogfreqscale(self, logfreqscale):
		if logfreqscale <> self.logfreqscale:
			print "freq scale changed", logfreqscale
			self.logfreqscale = logfreqscale
			self.update_xscale()
			self.erase()

	def addData(self, xyzs):
		if xyzs.ndim == 1:
			vsize = xyzs.shape[0]
			hsize = 1
		else:
			vsize = xyzs.shape[0]
			hsize = xyzs.shape[1]

		self.setvsize(vsize)

		for i in range(0, hsize):
			if hsize > 1:
				int_xyzs = self.interpolate(xyzs[:,-(i+1)])
			else:
				int_xyzs = self.interpolate(xyzs)
			self.addDataSingle(int_xyzs)

	def interpolate(self, xyzs):
		return numpy.interp(self.xscaled, self.x, xyzs)

	def addDataSingle(self, int_xyzs):
		debug = False

		# we start with fresh data, which will be consumed progressively
		available = 1.

		# until available gets zeroed, we have data to use
		while available > 0.: # FIXME why the following and i <10: # FIXME float comparison
			if debug: print "available ",  available

			# what is still needed before displaying : total number (n) minus what we have already got
			needed =  self.n - self.current_total
			if debug: print "needed",  needed

			# the current wavedata canot give more than what's not been used from it :
			current = min(needed,  available)
			if debug: print "current",  current

			# current_total will increase from 0 to n
			self.current_total += current
			if debug: print "self.current_total",  self.current_total

			# then we add the current data with the following weight (total weight will be one)
			weight = current/self.n
			if debug: print "weight",  weight
			self.xyzs_buffer += int_xyzs*weight

			# available is updated with what has just been used, (note that it should never go negative)
			available -= current

			# if current_total is n, we have successfully added enough data
			if self.current_total >= self.n:
				if debug: print "draw !"
				self.finish_line()

			if debug: print "finished !"

	def finish_line(self):
		# draw !
		byteString = self.floats_to_bytes(self.xyzs_buffer[::-1])

		myimage = self.prepare_image(byteString, self.xyzs_buffer.shape[0])

		self.offset = (self.offset + 1) % self.canvas_hsize
		self.painter.drawImage(self.offset, 0, myimage)
		self.painter.drawImage(self.offset + self.canvas_hsize, 0, myimage)
		# reinitialize current_total
		self.current_total = 0.
		# reinitialize the data buffer
		self.xyzs_buffer = numpy.zeros((self.canvas_vsize))

	def floats_to_bytes(self, data):
		#dat1 = (255. * data).astype(numpy.uint8)
		#dat4 = dat1.repeat(4)
		dat4 = self.color_from_float(data).astype(numpy.uint32)
		return dat4.tostring()

	def prepare_image(self, byteString, length):
		myimage = Qt.QImage(byteString, 1, length, Qt.QImage.Format_RGB32)
		return myimage

	def prepare_palette(self):
		self.colors = numpy.zeros((256))
		self.colorscale = numpy.linspace(0., 1., 256)
		for i in range(0, 256):
			self.colors[i] = self.colorMap.rgb(Qwt.QwtDoubleInterval(0,255), i)

	def color_from_float(self, v):
		d = numpy.digitize(v, self.colorscale)
		d = d + (d==len(self.colorscale))*(-1)
		return self.colors[d]
		#return numpy.interp(v, self.colorscale, self.colors)

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
