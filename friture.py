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

import sys
from pyaudio import PyAudio, paInt16
from numpy import transpose, log10, sqrt, ceil, linspace, arange
from PyQt4 import QtGui, QtCore, Qt
import PyQt4.Qwt5 as Qwt
from Ui_friture import Ui_MainWindow
import resource
import audiodata
import proc

#pyuic4 friture.ui > Ui_friture.py
#pyrcc4 resource.qrc > resource.py

#had to install pyqwt from source
#first : sudo ln -s libqwt-qt4.so libqwt.so
#then, in the pyqwt configure subdirectory (for ubuntu jaunty):
#python configure.py -Q ../qwt-5.1 -4 -L /usr/lib -I /usr/include/ --module-install-path=/usr/lib/python2.6/dist-packages/PyQt4/Qwt5
#make
#sudo make install

SAMPLING_RATE = 44100
NUM_SAMPLES = 1024
TIMER_PERIOD_MS = int(ceil(1000.*NUM_SAMPLES/float(SAMPLING_RATE)))
DEVICE_INDEX = 0

class Friture(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)

		# Configure l'interface utilisateur.
		self.setupUi(self)

		self.i = 0
		self.spec_min = -100.
		self.spec_max = -20.
		self.fft_size = 256

		print "Initializing PyAudio"
		self.pa = PyAudio()

		self.set_devices_list()
		device_count = self.get_device_count()
		default_device_index = self.get_default_input_device()
		
		# we will try to open all the devices until one works, starting by the default input device
		devices = range(0, device_count)
		devices.remove(default_device_index)
		devices = [default_device_index] + devices

		for index in devices:
			print "Opening the stream"
			self.stream = self.pa.open(format=paInt16, channels=1, rate=SAMPLING_RATE, input=True,
			frames_per_buffer=NUM_SAMPLES, input_device_index=index)

			print "Trying to read from the specified input device"
			n_try = 0
			while self.stream.get_read_available() < NUM_SAMPLES and n_try < 1000000:
				n_try +=1

			if n_try == 1000000:
				print "Fail"
			else:
				print "Success"
				break

		self.comboBox_inputDevice.setCurrentIndex(index)

		self.procclass = proc.ProcClass()
		self.canvasscaledspectrogram = audiodata.CanvasScaledSpectrogram()
		self.dest_pixmap = QtGui.QPixmap(600, 300)
		self.dest_pixmap.fill()
		self.painter = QtGui.QPainter(self.dest_pixmap)

		print "Setting up the timer"
		self.timer = QtCore.QTimer()
		#timer that fires roughly every 20 ms
		self.timer.setInterval(TIMER_PERIOD_MS)

		self.connect(self.pushButton_startstop, QtCore.SIGNAL('clicked()'), self.timer_toggle)
		self.connect(self.comboBox_freqscale, QtCore.SIGNAL('currentIndexChanged(int)'), self.freqscalechanged)
		self.connect(self.comboBox_fftsize, QtCore.SIGNAL('currentIndexChanged(int)'), self.fftsizechanged)
		self.connect(self.spinBox_specmax, QtCore.SIGNAL('valueChanged(int)'), self.specrangechanged)
		self.connect(self.spinBox_specmin, QtCore.SIGNAL('valueChanged(int)'), self.specrangechanged)
		self.connect(self.comboBox_inputDevice, QtCore.SIGNAL('currentIndexChanged(int)'), self.input_device_changed)
		self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.timer_slot)

		self.timer_toggle()
		print "Done"

	def timer_toggle(self):
		if self.timer.isActive():
			self.timer.stop()
		else:
			self.timer.start()

	def timer_slot(self):
		if self.stream.get_read_available() < NUM_SAMPLES:
			return
		
		while self.stream.get_read_available() >= NUM_SAMPLES:
			rawdata = self.stream.read(NUM_SAMPLES)

		channels = 1
		format = paInt16
		rate = SAMPLING_RATE
		adata = audiodata.AudioData(rawdata = rawdata,
					nchannels = channels,
					format = format,
					samplesize = self.pa.get_sample_size(format),
					samplerate = rate)

		self.i += 1
		time = adata.floatdata
		level_rms = 20*log10(sqrt((time**2).sum()/len(time)*2.) + 0*1e-80) #*2. to get 0dB for a sine wave
		level_max = 20*log10(abs(time).max() + 0*1e-80)
		level_label = "Chunk #%d\n%.01f dBFS RMS\n%.01f dBFS peak\n%.03f max" % (self.i, level_rms, level_max, time.max())
		self.LabelLevel.setText(level_label)

		self.meter.setValue(0, sqrt((time**2).sum()/len(time)*2.))
		self.meter.setValue(1, abs(time).max())

		signal = adata.floatdata
		time = linspace(0., len(signal)/float(rate), len(signal))
		
		self.PlotZoneUp.setdata(time, signal)

		sp = self.procclass.process(adata, self.fft_size)
		if sp == None:
			return

		clip = lambda val, low, high: min(high, max(low, val))
		# scale the db spectrum from [- spec_range db ... 0 db] > [0..1]
		epsilon = 1e-30
		db_spectrogram = (20*log10(sp + epsilon))
		norm_spectrogram = (db_spectrogram.clip(self.spec_min, self.spec_max) - self.spec_min)/(self.spec_max - self.spec_min)

		if db_spectrogram.ndim == 1:
			y = db_spectrogram.transpose()
		else:
			y = db_spectrogram[0,:].transpose()
		freq = linspace(0., 22050., len(y))
		self.PlotZoneSpect.setdata(freq, y)
		self.PlotZoneImage.addData(norm_spectrogram.transpose())

	def fftsizechanged(self, index):
		print "fft_size_changed slot", index, 2**index*32, 150000/self.fft_size
		self.fft_size = 2**index*32

	def freqscalechanged(self, index):
		print "freq_scale slot", index
		if index == 1:
			self.PlotZoneSpect.setlogfreqscale()
			self.PlotZoneImage.setlogfreqscale()
		else:
			self.PlotZoneSpect.setlinfreqscale()
			self.PlotZoneImage.setlinfreqscale()

	def specrangechanged(self, value):
		self.spec_max = self.spinBox_specmax.value()
		self.spec_min = self.spinBox_specmin.value()

	def set_devices_list(self):
		default_device_index = self.get_default_input_device()
		device_count = self.get_device_count()
		
		for i in range(0, device_count):
			dev = self.pa.get_device_info_by_index(i)
			api = self.pa.get_host_api_info_by_index(dev['hostApi'])['name']
			desc = "%d: (%s) %s" %(dev['index'], api, dev['name'])
			if i == default_device_index:
				desc += ' (system default)'			
			self.comboBox_inputDevice.addItem(desc)

	def get_default_input_device(self):
		return self.pa.get_default_input_device_info()['index']
	
	def get_device_count(self):
		return self.pa.get_device_count()

	def input_device_changed(self, index):
		print index
		self.timer_toggle()

		self.stream.close()
		self.stream = self.pa.open(format=paInt16, channels=1, rate=SAMPLING_RATE, input=True,
                     frames_per_buffer=NUM_SAMPLES, input_device_index=index)

		print "Trying to read from the specified input device"
		n_try = 0
		while self.stream.get_read_available() < NUM_SAMPLES and n_try < 1000000:
			n_try +=1

		if n_try == 1000000:
			print "Fail : exiting"
			sys.exit(0)
		else:
			print "Success"

		self.timer_toggle()

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)

	pixmap = QtGui.QPixmap(":/splash.png")
	splash = QtGui.QSplashScreen(pixmap)
	splash.show()
	splash.showMessage("Initializing the audio subsystem")
	app.processEvents()
	window = Friture()
	window.show()
	splash.finish(window)
	
	profile = True
	
	if profile:
		import cProfile
		import lsprofcalltree

		p = cProfile.Profile()
		p.run('app.exec_()')
		k = lsprofcalltree.KCacheGrind(p)
		data = open('prof.kgrind.out.00000', 'w+')
		k.output(data)
		data.close()
		sys.exit(0)
	else:
		sys.exit(app.exec_())
