# -*- coding: utf-8 -*-
import numpy
from PyQt4 import Qt, QtCore
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

class RawSpectrogram():
	def __init__(self, vsize = 0, hsize = 129):
		self.vsize = vsize
		self.hsize = hsize
		if self.vsize == 0:
			self.vsize = 2**18/((self.hsize-1)*2)
		self.fullspectrogram = numpy.zeros((self.hsize, self.vsize))
	def erase(self):
		self.fullspectrogram = numpy.zeros((self.hsize, self.vsize))
	def sethsize(self,hsize):
		if self.hsize <> hsize:
			self.hsize = hsize
			self.erase()
	def addData(self, xyzs):
		if xyzs.ndim == 1:
			hsize = xyzs.shape[0]
			vsize = 1
		else:
			hsize = xyzs.shape[0]
			vsize = xyzs.shape[1]

		if hsize<>self.hsize:
			self.sethsize(hsize)

		self.fullspectrogram = numpy.hstack((self.fullspectrogram[vsize:,:],xyzs))

	def data(self):
		return self.fullspectrogram

class FreqScaledSpectrogram():
	def __init__(self, vsize = 0, hsize = 129):
		self.hsize = hsize
		self.vsize = vsize
		if self.vsize == 0:
			self.vsize = 2**18/((self.hsize-1)*2)
		self.fullspectrogram = numpy.zeros((self.hsize, self.vsize))

	def erase(self):
		self.fullspectrogram = numpy.zeros((self.hsize, self.vsize))

	def sethsize(self,hsize):
		if self.hsize <> hsize:
			self.hsize = hsize
			self.erase()

	def addData(self, xyzs, logfreqscale = 0):
		if xyzs.ndim == 1:
			hsize = xyzs.shape[0]
			vsize = 1
		else:
			hsize = xyzs.shape[0]
			vsize = xyzs.shape[1]

		if hsize<>self.hsize:
			self.sethsize(hsize)

		if logfreqscale == 0:
			freqscaled_xyzs = xyzs #NOP
		else:
			# ideally, we should directly interpolate to the canvas vsize
			x = numpy.arange(0, hsize)*22050./hsize
			xlog = numpy.logspace(numpy.log10(20),numpy.log10(22050),hsize)

		if hsize == 1:
			freqscaled_xyzs = numpy.interp(xlog,x,xyzs)
		else:
			freqscaled_xyzs = numpy.interp(xlog,x,xyzs[0,:])

		for i in range(1,vsize):
		    freqscaled_xyzs = numpy.hstack((freqscaled_xyzs,numpy.interp(xlog,x,xyzs[i,:])))

		self.fullspectrogram = numpy.hstack((self.fullspectrogram[vsize:,:],freqscaled_xyzs))

	def data(self):
		return self.fullspectrogram

class CanvasScaledSpectrogram():
	def __init__(self, vsize = 129, hsize = 0, canvas_vsize = 2,  canvas_hsize = 2):
		self.hsize = hsize
		self.vsize = vsize
		if self.hsize == 0:
			# arbitrairement, pour le moment, on choisit que T/Dt vaut 2**18/((self.vsize-1)*2)
			# dans ces conditions, n = self.hsize/self.canvas_hsize
			self.hsize = 2**18/((self.vsize-1)*2)
		self.canvas_vsize = canvas_vsize
		self.canvas_hsize = canvas_hsize
		self.n = float(self.hsize)/canvas_hsize
		self.current_total = 0
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

	def erase(self):
		self.fullspectrogram = numpy.zeros((self.canvas_vsize, self.hsize, 4), dtype = numpy.uint8)
		self.xyzs_buffer = numpy.zeros((self.canvas_vsize))
		self.pixmap = Qt.QPixmap(2*self.canvas_hsize,  self.canvas_vsize)
		self.pixmap.fill(Qt.QColor("black"))
		self.painter = Qt.QPainter(self.pixmap)
		#self.spectrogramstr = ['\0']*self.canvas_vsize*self.vsize*4
		self.offset = 0

	def setvsize(self, vsize):
		if self.vsize <> vsize:
			print "vsize changed"
			self.vsize = vsize
			self.erase()

	def setcanvas_vsize(self, canvas_vsize):
		if self.canvas_vsize <> canvas_vsize:
			print "canvas_vsize changed",  canvas_vsize
			self.canvas_vsize = canvas_vsize
			self.erase()

	def setcanvas_hsize(self,canvas_hsize):
		if self.canvas_hsize <> canvas_hsize:
			self.canvas_hsize = canvas_hsize
			self.n = float(self.hsize)/canvas_hsize
			self.current_total = 0
			self.erase()
			print "canvas_hsize changed",  canvas_hsize,  self.n

	def addData(self, xyzs, logfreqscale = 0):
		if xyzs.ndim == 1:
			vsize = xyzs.shape[0]
			hsize = 1
		else:
			vsize = xyzs.shape[0]
			hsize = xyzs.shape[1]

		if vsize<>self.vsize:
			self.setvsize(vsize)

		x = numpy.arange(0, vsize)*22050./vsize
		
		if logfreqscale == 0:
			xscaled = numpy.arange(0, self.canvas_vsize)*22050./self.canvas_vsize
		else:
			xscaled = numpy.logspace(numpy.log10(20),numpy.log10(22050),self.canvas_vsize)

		for i in range(0,hsize):
			int_xyzs = numpy.interp(xscaled, x, xyzs[:,-(i+1)])

			debug = False

			# we start with fresh data, which will be consumed progressively
			available = 1.

			# until available gets zeroed, we have data to use
			while available > 0. and i <10: # FIXME float comparison
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
					# draw !
					if debug: print "draw !"
					dat1 = (255 * self.xyzs_buffer).astype(numpy.uint8)
					self.offset = (self.offset + 1) % self.canvas_hsize
					dat4 = dat1.repeat(4)
					self.byteString2 = dat4.tostring()
					myimage = Qt.QImage(self.byteString2, 1, dat1.shape[0], Qt.QImage.Format_Indexed8)
					for i in range(0, 256):
						myimage.setColor(i, Qt.qRgb(i, 0, 255-i)) # linear color
						myimage.setColor(i, self.colorMap.rgb(Qwt.QwtDoubleInterval(0,255),i)) # custom colormap
					self.painter.drawImage(self.offset, 0, myimage)
					self.painter.drawImage(self.offset + self.canvas_hsize, 0, myimage)
					# reinitialize current_total
					self.current_total = 0.
					# reinitialize the data buffer
					self.xyzs_buffer = numpy.zeros((self.canvas_vsize))

				if debug: print "finished !"

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

# une précision sur le nombre de fft à sommer
# la "vraie" restriction est donnée par la longueur de l'axe en secondes, notée T, éventuellement réglée par l'utilisateur, et le nombre de pixels correspondant W
# n=(T/W)/Dt
