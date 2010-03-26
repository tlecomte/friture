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

import sys, os, platform
from PyQt4 import QtGui, QtCore
from Ui_friture import Ui_MainWindow
import about # About dialog
import settings # Setting dialog
import logger # Logging class
import audiobuffer # audio ring buffer class
import audiobackend # audio backend class

#pyuic4 friture.ui > Ui_friture.py
#pyrcc4 resource.qrc > resource_rc.py

#had to install pyqwt from source
#first : sudo ln -s libqwt-qt4.so libqwt.so
#then, in the pyqwt configure subdirectory (for ubuntu jaunty):
#python configure.py -Q ../qwt-5.1 -4 -L /usr/lib -I /usr/include/ --module-install-path=/usr/lib/python2.6/dist-packages/PyQt4/Qwt5
#make
#sudo make install

#profiling:
#
#First option:
#python -m cProfile -o output.pstats ./friture.py
#./gprof2dot.py -f pstats output.pstats -n 0.1 -e 0.02| dot -Tpng -o output2.png
#
#second option:
# ./friture.py --python
# or
# ./friture.py --kcachegrind

#third option:
# use a system-wide profiler
# such as sysprof on Linux
# For sysprof, either use "sudo m-a a-i sysprof-module" to build the module for your current kernel,
# on Debian-like distributions, or use a development version of sysprof (>=1.11) and a recent
# kernel (>=2.6.31) that has built-in support, with in-kernel tracing as an addition
# ./gprof2dot.py -f sysprof sysprof_profile_kernel| dot -Tpng -o output_sysprof_kernel.png

# the sample rate below should be dynamic, taken from PyAudio/PortAudio
SAMPLING_RATE = 44100
SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25

class Friture(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self, logger):
		QtGui.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)

		# logger
		self.logger = logger

		# Setup the user interface
		self.setupUi(self)
		
		self.settings_dialog = settings.Settings_Dialog()
		self.about_dialog = about.About_Dialog()
		
		levelsAction = self.dockWidgetLevels.toggleViewAction()
		scopeAction = self.dockWidgetScope.toggleViewAction()
		spectrumAction = self.dockWidgetSpectrum.toggleViewAction()
		statisticsAction = self.dockWidgetStatistics.toggleViewAction()
		logAction = self.dockWidgetLog.toggleViewAction()
		
		levelsAction.setIcon(QtGui.QIcon(":/levels.svg"))
		scopeAction.setIcon(QtGui.QIcon(":/scope.svg"))
		spectrumAction.setIcon(QtGui.QIcon(":/spectrum.svg"))
		statisticsAction.setIcon(QtGui.QIcon(":/statistics.svg"))
		logAction.setIcon(QtGui.QIcon(":/log.svg"))
		
		self.toolBar.addAction(levelsAction)
		self.toolBar.addAction(scopeAction)
		self.toolBar.addAction(spectrumAction)
		self.toolBar.addAction(statisticsAction)
		self.toolBar.addAction(logAction)
		
		self.chunk_number = 0
		
		self.display_timer_time = 0.
		self.buffer_timer_time = 0.

		# Initialize the audio data ring buffer
		self.audiobuffer = audiobuffer.AudioBuffer()

		# Initialize the audio backend
		self.audiobackend = audiobackend.AudioBackend(self.logger)
		
		devices = self.audiobackend.get_devices()
		for dev in devices:
			self.settings_dialog.comboBox_inputDevice.addItem(dev)

		current_device = self.audiobackend.get_current_device()
		self.settings_dialog.comboBox_inputDevice.setCurrentIndex(current_device)

		# this timer is used to update widgets that just need to display as fast as they can
		self.display_timer = QtCore.QTimer()
		self.display_timer.setInterval(SMOOTH_DISPLAY_TIMER_PERIOD_MS) # constant timing

		# timer ticks
		self.connect(self.display_timer, QtCore.SIGNAL('timeout()'), self.display_timer_slot)
		
		# toolbar clicks
		self.connect(self.actionStart, QtCore.SIGNAL('triggered()'), self.timer_toggle)
		self.connect(self.actionSettings, QtCore.SIGNAL('triggered()'), self.settings_called)
		self.connect(self.actionAbout, QtCore.SIGNAL('triggered()'), self.about_called)
		
		# settings signals
		self.connect(self.settings_dialog.comboBox_inputDevice, QtCore.SIGNAL('currentIndexChanged(int)'), self.input_device_changed)

		# log change
		self.connect(self.logger, QtCore.SIGNAL('logChanged'), self.log_changed)
		self.connect(self.scrollArea_2.verticalScrollBar(), QtCore.SIGNAL('rangeChanged(int,int)'), self.log_scroll_range_changed)
		
		# restore the settings and widgets geometries
		self.restoreAppState()

		# start timers
		self.timer_toggle()
		
		self.logger.push("Init finished, entering the main loop")
	
	# slot
	# update the log widget with the new log content
	def log_changed(self):
		self.LabelLog.setText(self.logger.text())
	
	# slot
	# scroll the log widget so that the last line is visible
	def log_scroll_range_changed(self, min, max):
		scrollbar = self.scrollArea_2.verticalScrollBar()
		scrollbar.setValue(max)
	
	# slot
	def settings_called(self):
		self.settings_dialog.show()
	
	# slot
	def about_called(self):
		self.about_dialog.show()
	
	# event handler
	def closeEvent(self, event):
		self.saveAppState()
		event.accept()
	
	# method
	def saveAppState(self):
		windowState = self.saveState()
		settings = QtCore.QSettings("Friture", "Friture")
		
		settings.beginGroup("MainWindow")
		settings.setValue("windowState", windowState)
		
		settings.beginGroup("Spectrogram")
		self.spectrogram.saveState(settings)
		
		settings.beginGroup("Spectrum")
		self.spectrum.saveState(settings)
		
		settings.endGroup()
	
	# method
	def restoreAppState(self):
		settings = QtCore.QSettings("Friture", "Friture")
		
		settings.beginGroup("MainWindow")
		self.restoreState(settings.value("windowState").toByteArray())
		
		settings.beginGroup("Spectrogram")
		self.spectrogram.restoreState(settings)

		settings.beginGroup("Spectrum")
		self.spectrum.restoreState(settings)

		settings.endGroup()

	# slot
	def timer_toggle(self):
		if self.display_timer.isActive():
			self.logger.push("Timer stop")
			self.display_timer.stop()
			self.spectrogram.timer.stop()
		else:
			self.logger.push("Timer start")
			self.display_timer.start()
			self.spectrogram.timer.start()

	# slot
	def display_timer_slot(self):
		(chunks, t) = self.audiobuffer.update(self.audiobackend.stream)
		self.chunk_number += chunks
		self.buffer_timer_time = (95.*self.buffer_timer_time + 5.*t)/100.
		
		t = QtCore.QTime()
		t.start()
		
		self.statistics()
		
		self.levels.update(self.audiobuffer)
		
		self.scope.update(self.audiobuffer)
		
		self.spectrum.update(self.audiobuffer)
		
		self.display_timer_time = (95.*self.display_timer_time + 5.*t.elapsed())/100.

	# method
	def statistics(self):
		if not self.LabelLevel.isVisible():
		    return
		    
		level_label = "Chunk #%d\n"\
		"FFT period : %.01f ms\n"\
		"Spectrogram timer period : %.01f ms\n"\
		"Levels, scope and spectrum computation: %.02f ms\n"\
		"Spectrogram computation: %.02f ms\n"\
		"Audio buffer retrieval: %.02f ms\n"\
		"Levels painting: %.02f ms and %.02f ms\n"\
		"Scope painting: %.02f ms\n"\
		"Spectrum painting: %.02f ms\n"\
		"Spectrogram painting: %.02f ms"\
		% (self.chunk_number,
		self.spectrum.fft_size*1000./SAMPLING_RATE,
		self.spectrogram.period_ms,
		self.display_timer_time,
		self.spectrogram.spectrogram_timer_time,
		self.buffer_timer_time,
		self.levels.meter.m_ppValues[0].paint_time,
		self.levels.meter.m_ppValues[1].paint_time,
		self.scope.PlotZoneUp.paint_time,
		self.spectrum.PlotZoneSpect.paint_time,
		self.spectrogram.PlotZoneImage.paint_time)
		
		self.LabelLevel.setText(level_label)

	# slot
	def input_device_changed(self, index):
		self.display_timer.stop()
		self.spectrogram.timer.stop()
		self.actionStart.setChecked(False)
		
		success, index = self.audiobackend.select_input_device(index)
		
		self.settings_dialog.comboBox_inputDevice.setCurrentIndex(index)
		
		if not success:
			error_message = QtGui.QErrorMessage(self)
			error_message.setWindowTitle("Input device error")
			error_message.showMessage("Impossible to use the selected device, reverting to the previous one")
		
		self.display_timer.start()
		self.spectrogram.timer.start()
		self.actionStart.setChecked(True)

if __name__ == "__main__":
	if platform.system() == "Windows":
		print "Running on Windows"
		# On Windows, redirect stderr to a file
		import imp, ctypes
		if (hasattr(sys, "frozen") or # new py2exe
			hasattr(sys, "importers") or # old py2exe
			imp.is_frozen("__main__")): # tools/freeze
				sys.stderr = open(os.path.expanduser("~/friture.exe.log"), "w")
		# set the App ID for Windows 7 to properly display the icon in the
		# taskbar.
		myappid = 'Friture.Friture.Friture.current' # arbitrary string
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

	app = QtGui.QApplication(sys.argv)

	# Splash screen
	pixmap = QtGui.QPixmap(":/splash.png")
	splash = QtGui.QSplashScreen(pixmap)
	splash.show()
	splash.showMessage("Initializing the audio subsystem")
	app.processEvents()
	
	# Logger class
	logger = logger.Logger()
	
	window = Friture(logger)
	window.show()
	splash.finish(window)
	
	profile = "no" # "python" or "kcachegrind" or anything else to disable

	if len(sys.argv) > 1:
		if sys.argv[1] == "--python":
			profile = "python"
		elif sys.argv[1] == "--kcachegrind":
			profile = "kcachegrind"
		elif sys.argv[1] == "--no":
			profile = "no"
		else:
			print "command-line arguments (%s) not recognized" %sys.argv[1:]

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
