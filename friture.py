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
from numpy import transpose, log10, sqrt, ceil, linspace, arange, floor, zeros, int32, fromstring
import math
from PyQt4 import QtGui, QtCore, Qt
import PyQt4.Qwt5 as Qwt
from Ui_friture import Ui_MainWindow
import resource_rc
import audiodata
import audioproc

#pyuic4 friture.ui > Ui_friture.py
#pyrcc4 resource.qrc > resource_rc.py

#had to install pyqwt from source
#first : sudo ln -s libqwt-qt4.so libqwt.so
#then, in the pyqwt configure subdirectory (for ubuntu jaunty):
#python configure.py -Q ../qwt-5.1 -4 -L /usr/lib -I /usr/include/ --module-install-path=/usr/lib/python2.6/dist-packages/PyQt4/Qwt5
#make
#sudo make install

SAMPLING_RATE = 44100
NUM_SAMPLES = 1024
FRAMES_PER_BUFFER = NUM_SAMPLES
TIMER_PERIOD_MS = int(ceil(1000.*NUM_SAMPLES/float(SAMPLING_RATE)))
SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
DEVICE_INDEX = 0

class Friture(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)

		# Configure l'interface utilisateur.
		self.setupUi(self)
		
		levelsAction = self.dockWidgetLevels.toggleViewAction()
		scopeAction = self.dockWidgetScope.toggleViewAction()
		spectrumAction = self.dockWidgetSpectrum.toggleViewAction()
		statisticsAction = self.dockWidgetStatistics.toggleViewAction()
		
		levelsAction.setIcon(QtGui.QIcon(":/levels.svg"))
		scopeAction.setIcon(QtGui.QIcon(":/scope.svg"))
		spectrumAction.setIcon(QtGui.QIcon(":/spectrum.svg"))
		statisticsAction.setIcon(QtGui.QIcon(":/statistics.svg"))
		
		self.toolBar.addAction(levelsAction)
		self.toolBar.addAction(scopeAction)
		self.toolBar.addAction(spectrumAction)
		self.toolBar.addAction(statisticsAction)
		
		self.scopeIsVisible = True
		self.statisticsIsVisible = True
		self.levelsIsVisible = True
		self.spectrumIsVisible = True

		self.i = 0
		self.losts = 0
		self.useless = 0
		self.spec_min = -100.
		self.spec_max = -20.
		self.fft_size = 256
		self.max_in_a_row = 1
		self.time = QtCore.QTime()
		self.time.start()
		self.latency = 0.
		self.mean_chunks_per_fire = 0.
		self.timerange_s = 10.
		self.canvas_width = 100.
		
		self.buffer_length = 100000.
		self.audiobuffer = zeros(2*self.buffer_length)
		self.offset = 0

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
			frames_per_buffer=FRAMES_PER_BUFFER, input_device_index=index)
			self.device_index = index

			print "Trying to read from input device #%d" % (index)
			if self.try_input_device():
				print "Success"
				lat_ms = 1000*self.stream.get_input_latency()
				self.max_in_a_row = int(ceil(lat_ms/TIMER_PERIOD_MS))
				break
			else:
				print "Fail"

		self.comboBox_inputDevice.setCurrentIndex(self.device_index)

		# this timer is used to update widgets that just need to display as fast as they can
		self.display_timer = QtCore.QTimer()
		self.display_timer.setInterval(SMOOTH_DISPLAY_TIMER_PERIOD_MS) # constant timing

		# this timer is used to update the spectrogram widget, whose update period
		# is fixed by the time scale and the width of the widget canvas
		self.spectrogram_timer = QtCore.QTimer()
		self.spectrogram_timer.setInterval(SMOOTH_DISPLAY_TIMER_PERIOD_MS) # variable timing

		self.connect(self.display_timer, QtCore.SIGNAL('timeout()'), self.display_timer_slot)
		self.connect(self.spectrogram_timer, QtCore.SIGNAL('timeout()'), self.spectrogram_timer_slot)
		
		self.connect(self.actionStart, QtCore.SIGNAL('triggered()'), self.timer_toggle)
		
		self.connect(self.comboBox_freqscale, QtCore.SIGNAL('currentIndexChanged(int)'), self.freqscalechanged)
		self.connect(self.comboBox_fftsize, QtCore.SIGNAL('currentIndexChanged(int)'), self.fftsizechanged)
		self.connect(self.spinBox_specmax, QtCore.SIGNAL('valueChanged(int)'), self.specrangechanged)
		self.connect(self.spinBox_specmin, QtCore.SIGNAL('valueChanged(int)'), self.specrangechanged)
		self.connect(self.doubleSpinBox_timerange, QtCore.SIGNAL('valueChanged(double)'), self.timerangechanged)
		self.connect(self.spinBox_minfreq, QtCore.SIGNAL('valueChanged(int)'), self.freqrangechanged)
		self.connect(self.spinBox_maxfreq, QtCore.SIGNAL('valueChanged(int)'), self.freqrangechanged)
		self.connect(self.comboBox_inputDevice, QtCore.SIGNAL('currentIndexChanged(int)'), self.input_device_changed)
		
		self.connect(self.PlotZoneImage, QtCore.SIGNAL('pointerMoved'), self.pointer_moved)
		self.connect(self.PlotZoneSpect, QtCore.SIGNAL('pointerMoved'), self.pointer_moved)
		self.connect(self.PlotZoneUp, QtCore.SIGNAL('pointerMoved'), self.pointer_moved)
		
		self.connect(self.dockWidgetScope, QtCore.SIGNAL('visibilityChanged(bool)'), self.scopeVisibility)
		self.connect(self.dockWidgetStatistics, QtCore.SIGNAL('visibilityChanged(bool)'), self.statisticsVisibility)
		self.connect(self.dockWidgetLevels, QtCore.SIGNAL('visibilityChanged(bool)'), self.levelsVisibility)
		self.connect(self.dockWidgetSpectrum, QtCore.SIGNAL('visibilityChanged(bool)'), self.spectrumVisibility)

		self.connect(self.PlotZoneImage.plotImage.canvasscaledspectrogram, QtCore.SIGNAL("canvasWidthChanged"), self.canvasWidthChanged)
		
		self.restoreAppState()

		# start timers
		self.timer_toggle()
		
		print "Init finished, entering the main loop"
	
	def closeEvent(self, event):
		self.saveAppState()
		event.accept()
	
	def saveAppState(self):
		windowState = self.saveState()
		settings = QtCore.QSettings("Friture", "Friture")
		
		settings.beginGroup("MainWindow")
		settings.setValue("windowState", windowState)
		
		settings.beginGroup("Audio")
		settings.setValue("fftSize", self.fft_size)
		settings.setValue("freqScale", self.freqscale)
		settings.setValue("freqMin", self.spinBox_minfreq.value())
		settings.setValue("freqMax", self.spinBox_maxfreq.value())
		settings.setValue("timeRange", self.doubleSpinBox_timerange.value())
		
		settings.endGroup()
	
	def restoreAppState(self):
		settings = QtCore.QSettings("Friture", "Friture")
		
		settings.beginGroup("MainWindow")
		self.restoreState(settings.value("windowState").toByteArray())
		
		settings.beginGroup("Audio")
		(fft_size, ok) = settings.value("fftSize", 256).toInt()
		self.comboBox_fftsize.setCurrentIndex(math.log(fft_size/32,2))
		(freqscale, ok) = settings.value("freqScale", 0).toInt()
		self.comboBox_freqscale.setCurrentIndex(freqscale)
		(freqMin, ok) = settings.value("freqMin", 20).toInt()
		self.spinBox_minfreq.setValue(freqMin)
		(freqMax, ok) = settings.value("freqMax", 20000).toInt()
		self.spinBox_maxfreq.setValue(freqMax)
		(timeRange, ok) = settings.value("timeRange", 10.).toDouble()
		self.doubleSpinBox_timerange.setValue(timeRange)
		
		settings.endGroup()

	def scopeVisibility(self, visible):
		self.scopeIsVisible = visible
	
	def statisticsVisibility(self, visible):
		self.statisticsIsVisible = visible

	def levelsVisibility(self, visible):
		self.levelsIsVisible = visible

	def spectrumVisibility(self, visible):
		self.spectrumIsVisible = visible

	def pointer_moved(self, info):
		self.statusBar.showMessage(info)

	#return True on success
	def try_input_device(self):
		n_try = 0
		while self.stream.get_read_available() < NUM_SAMPLES and n_try < 1000000:
			n_try +=1

		if n_try == 1000000:
			return False
		else:
			lat_ms = 1000*self.stream.get_input_latency()
			print "Device claims %d ms latency" %(lat_ms)
			return True

	def timer_toggle(self):
		print "toggle"
		if self.display_timer.isActive():
			self.display_timer.stop()
			self.spectrogram_timer.stop()
		else:
			self.display_timer.start()
			self.spectrogram_timer.start()

	def display_timer_slot(self):
		self.update_buffer()
		
		if self.statisticsIsVisible:
			self.statistics()
		
		if self.levelsIsVisible:
			time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000.
			start = self.offset + self.buffer_length - time*SAMPLING_RATE
			stop = self.offset + self.buffer_length
			self.levels(self.audiobuffer[start : stop])
		
		if self.scopeIsVisible:
			time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000.
			start = self.offset + self.buffer_length - time*SAMPLING_RATE
			stop = self.offset + self.buffer_length
			self.scope(self.audiobuffer[start : stop], SAMPLING_RATE)
		
		if self.spectrumIsVisible:
			sp = audioproc.analyzelive(self.audiobuffer[self.offset + self.buffer_length - self.fft_size: self.offset + self.buffer_length], self.fft_size)
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

	def spectrogram_timer_slot(self):
		self.update_buffer()

		sp = audioproc.analyzelive(self.audiobuffer[self.offset + self.buffer_length - self.fft_size: self.offset + self.buffer_length], self.fft_size)
		clip = lambda val, low, high: min(high, max(low, val))
		# scale the db spectrum from [- spec_range db ... 0 db] > [0..1]
		epsilon = 1e-30
		db_spectrogram = (20*log10(sp + epsilon))
		norm_spectrogram = (db_spectrogram.clip(self.spec_min, self.spec_max) - self.spec_min)/(self.spec_max - self.spec_min)
		
		self.PlotZoneImage.addData(norm_spectrogram.transpose())

	def update_buffer(self):
		debug = False
		if debug: print "update_buffer"
		# ask for how much data is available
		available = self.stream.get_read_available()
		if debug: print "available", available
		# read what is available
		if debug: print "about to read"
		# we read by multiples of NUM_SAMPLES
		available = int(floor(available/NUM_SAMPLES))
		for j in range(0, available):
			self.i += 1
			rawdata = self.stream.read(NUM_SAMPLES)
			floatdata = fromstring(rawdata, int32)/2.**31
			# update the circular buffer
			if debug: print "available", available, "buffer length", self.buffer_length
			if len(floatdata) > self.buffer_length:
				print "buffer error"
				exit(1)
			
			# first copy, always complete
			self.audiobuffer[self.offset : self.offset + len(floatdata)] = floatdata[:]
			# second copy, can be folded
			direct = min(len(floatdata), self.buffer_length - self.offset)
			folded = len(floatdata) - direct
			if debug: print "direct", direct, "folded", folded
			self.audiobuffer[self.offset + self.buffer_length: self.offset + self.buffer_length + direct] = floatdata[0 : direct]
			self.audiobuffer[:folded] = floatdata[direct:]
			
			self.offset = int((self.offset + len(floatdata)) % self.buffer_length)
			if debug: print "new offset", self.offset

	#def timer_slot(self):
		#return
		#available = self.stream.get_read_available()
		#available = int(floor(available/NUM_SAMPLES))
		
		#if available == 0:
			#self.useless += 1
			#return
		
		#self.latency = self.time.restart()
		
		#jmax = min(available, self.max_in_a_row)
		#self.losts += available - jmax
		
		#self.last = False
		
		#for j in range(0, jmax):
			#rawdata = self.stream.read(NUM_SAMPLES)
			#if j == jmax-1:
				#self.last = True
			#self.process_data(rawdata)
		
		## discard the rest of the data that we cannot reasonably process
		#for j in range(jmax, available):
			#rawdata = self.stream.read(NUM_SAMPLES)
		
		#if self.mean_chunks_per_fire == 0:
			#self.mean_chunks_per_fire = jmax
		#else:
			#mean_number = min(self.i, 1000.)
			#self.mean_chunks_per_fire = (self.mean_chunks_per_fire*mean_number + jmax)/(mean_number + 1.)

	def statistics(self):
		level_label = "Chunk #%d\n"\
		"Lost chunks: %d = %.01f %%\n"\
		"Useless timer wakeups: %d = %.01f %%\n"\
		"Latency: %d ms\n"\
		"Mean number of chunks per timer fire: %.01f\n"\
		"FFT period : %.01f ms"\
		% (self.i,
		self.losts,
		self.losts*100./float(self.i),
		self.useless, self.useless*100./float(self.i),
		self.latency,
		self.mean_chunks_per_fire,
		self.fft_size*1000./SAMPLING_RATE)
		self.LabelLevel.setText(level_label)

	def levels(self, floatdata):
		level_rms = 20*log10(sqrt((floatdata**2).sum()/len(floatdata)*2.) + 0*1e-80) #*2. to get 0dB for a sine wave
		level_max = 20*log10(abs(floatdata).max() + 0*1e-80)
		self.label_rms.setText("%.01f" % level_rms)
		self.label_peak.setText("%.01f" % level_max)
		self.meter.setValue(0, sqrt((floatdata**2).sum()/len(floatdata)*2.))
		self.meter.setValue(1, abs(floatdata).max())

	def scope(self, floatdata, rate):
		time = linspace(0., len(floatdata)/float(rate), len(floatdata))
		self.PlotZoneUp.setdata(time, floatdata)

	def fftsizechanged(self, index):
		print "fft_size_changed slot", index, 2**index*32, 150000/self.fft_size
		self.fft_size = 2**index*32

	def freqscalechanged(self, index):
		print "freq_scale slot", index
		self.freqscale = index
		if self.freqscale == 2:
			self.PlotZoneSpect.setlogfreqscale()
			print "Warning: Spectrum widget still in base 10 logarithmic"
			self.PlotZoneImage.setlog2freqscale()
		elif index == 1:
			self.PlotZoneSpect.setlogfreqscale()
			self.PlotZoneImage.setlog10freqscale()
		else:
			self.PlotZoneSpect.setlinfreqscale()
			self.PlotZoneImage.setlinfreqscale()

	def freqrangechanged(self, value):
		minfreq = self.spinBox_minfreq.value()
		maxfreq = self.spinBox_maxfreq.value()
		self.PlotZoneSpect.setfreqrange(minfreq, maxfreq)
		self.PlotZoneImage.setfreqrange(minfreq, maxfreq)

	def specrangechanged(self, value):
		self.spec_max = self.spinBox_specmax.value()
		self.spec_min = self.spinBox_specmin.value()
		
	def timerangechanged(self, value):
		self.timerange_s = value
		self.PlotZoneImage.settimerange(value)
		self.reset_timer()
	
	def canvasWidthChanged(self, width):
		self.canvas_width = width
		self.reset_timer()
		
	def reset_timer(self):
		# FIXME millisecond resolution is limiting !
		# need to find a way to integrate this cleverly in the GUI
		# When the period is smaller than 25 ms, we can reasonably
		# try to draw as many columns at once as possible
		period_ms = 1000.*self.timerange_s/self.canvas_width
		print "Resetting the timer, will fire every %d ms" %(period_ms)
		self.spectrogram_timer.setInterval(period_ms)
		
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
		self.display_timer.stop()
		self.spectrogram_timer.stop()
		self.actionStart.setChecked(False)
		
		# save current stream in case we need to restore it
		previous_stream = self.stream

		self.stream = self.pa.open(format=paInt16, channels=1, rate=SAMPLING_RATE, input=True,
                     frames_per_buffer=FRAMES_PER_BUFFER, input_device_index=index)

		print "Trying to read from input device #%d" % (index)
		if self.try_input_device():
			print "Success"
			previous_stream.close()
			self.device_index = index
		else:
			print "Fail"
			error_message = QtGui.QErrorMessage(self)
			error_message.setWindowTitle("Input device error")
			error_message.showMessage("Impossible to use the selected device, reverting to the previous one")
			self.stream.close()
			self.stream = previous_stream
			self.comboBox_inputDevice.setCurrentIndex(self.device_index)
		
		lat_ms = 1000*self.stream.get_input_latency()
		self.max_in_a_row = int(ceil(lat_ms/TIMER_PERIOD_MS))
		
		self.display_timer.start()
		self.spectrogram_timer.start()
		self.actionStart.setChecked(True)

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
	
	profile = "no" # "python" or "kcachegrind" or anything else to disable
	
	if profile == "python":
		import cProfile
		import pstats
		
		cProfile.run('app.exec_()',filename="friture.cprof")
		
		stats = pstats.Stats("friture.cprof")
		stats.strip_dirs().sort_stats('time').print_stats(20)
		
		sys.exit(0)
	elif profile == "kcachegrind":
		import cProfile
		import lsprofcalltree

		p = cProfile.Profile()
		p.run('app.exec_()')
		k = lsprofcalltree.KCacheGrind(p)
		data = open('cachegrind.out.00000', 'w+')
		k.output(data)
		data.close()
		
		sys.exit(0)
	else:
		sys.exit(app.exec_())
