#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2.0 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

import pyaudio
import wave
import sys
import numpy
from PyQt4 import QtGui, QtCore, Qt
from Ui_friture import Ui_MainWindow
import PyQt4.Qwt5 as Qwt
import audiodata
import acqthread
import procthread
import Image

class Friture(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		
		# Configure l'interface utilisateur.
		self.setupUi(self)
		
		self.connect(self.pushButton_start, QtCore.SIGNAL('clicked()'), self.getaudio)
		self.connect(self.pushButton_stop, QtCore.SIGNAL('clicked()'), self.stop_record)
		self.connect(self.comboBox_freqscale, QtCore.SIGNAL('currentIndexChanged(int)'), self.freqscalechanged)
		self.connect(self.comboBox_fftsize, QtCore.SIGNAL('currentIndexChanged(int)'), self.fftsizechanged)
		self.connect(self.spinBox_specmax, QtCore.SIGNAL('valueChanged(int)'), self.specrangechanged)
		self.connect(self.spinBox_specmin, QtCore.SIGNAL('valueChanged(int)'), self.specrangechanged)
		
		self.thread = acqthread.AcqThread()
		self.connect(self.thread, QtCore.SIGNAL("recorded_time"), self.record_slot_time)
		self.connect(self.thread, QtCore.SIGNAL("recorded_freq"), self.record_slot_freq)
		
		self.procthread = procthread.ProcThread()
		self.connect(self.procthread, QtCore.SIGNAL("recorded_freq"), self.record_slot_freq)
		
		self.FORMAT = pyaudio.paInt32
		self.CHANNELS = 1
		self.RATE = 44100
		self.fft_size = 256
		
		self.spec_min = -100.
		self.spec_max = -20.
		
		self.started = False
		
		self.display_overflow = 0
		
		self.printinfos()
		
		self.PlotZoneSpect.setAxisScale(Qwt.QwtPlot.yLeft, -180., 0.)
		self.PlotZoneSpect.setAxisTitle(Qwt.QwtPlot.xBottom, 'Frequency (Hz)')
		self.PlotZoneSpect.setAxisTitle(Qwt.QwtPlot.yLeft, 'PSD (dBFS)')
		self.PlotZoneSpect.setAxisScale(Qwt.QwtPlot.xBottom, 20., 22050.)
		
		self.PlotZoneUp.setAxisTitle(Qwt.QwtPlot.xBottom, 'Time (s)')
		self.PlotZoneUp.setAxisTitle(Qwt.QwtPlot.yLeft, 'Signal')
		
		self.PlotLevel.setRange(-180,0)

	def printinfos(self):
		print "APIs list :"
		
		#api_number = self.p.get_host_api_count()
		#for i in range(0,api_number):
			#print self.p.get_host_api_info_by_index(i)
	
		#print "Devices list :"
	
		#dev_number = self.p.get_device_count()
		#for i in range(0,dev_number):
			#print self.p.get_device_info_by_index(i)
	
		#print "Default input device :"
		#print self.p.get_default_input_device_info()

	def getaudio(self):
		self.started = True
		self.thread.record(self.FORMAT, self.CHANNELS, self.RATE, self.fft_size)
	
	def stop_record(self):
		print "stop record"
		self.started = False
		self.thread.recordstop()

	def record_slot_time(self, data, sigcount):
		if sigcount < self.thread.read_signal_count():
			self.display_overflow += 1
			if self.display_overflow%20 == 0:
				print "display_overflow", self.display_overflow
			self.overflow = True
		else:
			self.overflow = False
		#	self.overflow = False

		self.update_time_plot(data.floatdata)
	
		level = 20*numpy.log10(numpy.sqrt((data.floatdata**2).sum())/len(data.floatdata) + 1e-60)
		self.update_level(level)

		self.procthread.process(data, self.fft_size)

	def update_level(self, level):
		# this could go in a specific plot widget class
		self.PlotLevel.setValue(level)
		level_label = "%.01f dBFS" % level
		self.LabelLevel.setText(level_label)

	def update_time_plot(self, floatdata):
		# this could go in a specific plot widget class

		#warning: downsampling makes the waveform unrealistic
		#downsampled_data = floatdata[:(len(floatdata)/200)*200]
		#downsampled_data = downsampled_data.reshape(200,len(floatdata)/200)
		#downsampled_data = downsampled_data.sum(axis=1)
		#x = numpy.arange(0, len(downsampled_data))*len(floatdata)/(float(self.RATE)*len(downsampled_data))
		x = numpy.arange(0, len(floatdata))/float(self.RATE)
		self.PlotZoneUp.setAxisScale(Qwt.QwtPlot.xBottom, 0., x.max())
		self.PlotZoneUp.setdata(x, floatdata)
		#self.PlotZoneUp.setdata(x, downsampled_data)

	def record_slot_freq(self, spectrogram):#, sigcount, sigcountperacq):
		#print "record_slot"
		#if sigcount < self.thread.read_signal_count() - sigcountperacq:
			#self.display_overflow += 1
			#print "display_overflow", self.display_overflow, sigcountperacq
			#return
		if not self.overflow:
			clip = lambda val, low, high: min(high, max(low, val))
			# scale the db spectrum from [- spec_range db ... 0 db] > [0..1]
			epsilon = 1e-30
			db_spectrogram = (20*numpy.log10(spectrogram + epsilon))
			norm_spectrogram = (db_spectrogram.clip(self.spec_min, self.spec_max) - self.spec_min)/(self.spec_max - self.spec_min)

			if db_spectrogram.ndim == 1:
				y = db_spectrogram.transpose()
			else:
				y = db_spectrogram[0,:].transpose()
			x = numpy.arange(0, len(y))*22050./len(y)
			self.PlotZoneSpect.setdata(x, y)

			self.PlotZoneImage.addData(norm_spectrogram.transpose())
	
	def fftsizechanged(self,index):
		print "fft_size_changed slot", index, 2**index*32, 150000/self.fft_size
		self.fft_size = 2**index*32
		if self.started:
			self.getaudio()

	def freqscalechanged(self,index):
		print "freq_scale slot", index
		if index == 1:
			self.PlotZoneSpect.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLog10ScaleEngine())
			self.PlotZoneImage.setlogfreqscale()
		else:
			self.PlotZoneSpect.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLinearScaleEngine())
			self.PlotZoneImage.setlinfreqscale()

	def specrangechanged(self,value):
		self.spec_max = self.spinBox_specmax.value()
		self.spec_min = self.spinBox_specmin.value()

	def store(self):
		self.WAVE_OUTPUT_FILENAME = "output.wav"
		print "saving"
		wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
		wf.setnchannels(self.audiodata.nchannels)
		wf.setsampwidth(self.audiodata.samplesize)
		wf.setframerate(self.audiodata.samplerate)
		wf.writeframes(self.audiodata.rawdata)
		wf.close()

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = Friture()
	window.show()
	
	profile = True
	
	if profile:
		import cProfile
		import lsprofcalltree

		p = cProfile.Profile()
		p.run('app.exec_()')
		k = lsprofcalltree.KCacheGrind(p)
		data = open('prof.kgrind.out', 'w+')
		k.output(data)
		data.close()
		sys.exit(0)
	else:
		sys.exit(app.exec_())
