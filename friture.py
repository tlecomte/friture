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
from dock import Dock
import about # About dialog
import settings # Setting dialog
import logger # Logging class
import audiobuffer # audio ring buffer class
import audiobackend # audio backend class
from centralwidget import CentralWidget
import psutil # for CPU usage monitoring

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

STYLESHEET = """
"""
#QMainWindow::separator {
#background: black;
#width: 1px;
#height: 1px;
#}
#
#QMainWindow::separator:hover {
#background: black;
#width: 1px;
#height: 1px;
#}
#
#QToolBar {
#border: none;
#background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#stop: 0 #a6a6a6, stop: 0.08 #7f7f7f,
#stop: 0.39999 #717171, stop: 0.4 #626262,
#stop: 0.9 #4c4c4c, stop: 1 #333333);
#}
#
#QToolButton {
#color: white;
#}
#"""

class Friture(QtGui.QMainWindow, ):
	def __init__(self, logger):
		QtGui.QMainWindow.__init__(self)

		Ui_MainWindow.__init__(self)

		# logger
		self.logger = logger

		# Setup the user interface
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		
		self.settings_dialog = settings.Settings_Dialog()
		self.about_dialog = about.About_Dialog()
		
		statisticsAction = self.ui.dockWidgetStatistics.toggleViewAction()
		logAction = self.ui.dockWidgetLog.toggleViewAction()
		
		statisticsAction.setIcon(QtGui.QIcon(":/statistics.svg"))
		logAction.setIcon(QtGui.QIcon(":/log.svg"))
		
		self.ui.toolBar.addAction(statisticsAction)
		self.ui.toolBar.addAction(logAction)
		
		self.chunk_number = 0
		
		self.buffer_timer_time = 0.
		
		self.cpu_percent = 0.

		# Initialize the audio data ring buffer
		self.audiobuffer = audiobuffer.AudioBuffer()

		# Initialize the audio backend
		self.audiobackend = audiobackend.AudioBackend(self.logger)
		
		devices = self.audiobackend.get_devices()
		for dev in devices:
			self.settings_dialog.comboBox_inputDevice.addItem(dev)

		current_device = self.audiobackend.get_current_device()
		self.settings_dialog.comboBox_inputDevice.setCurrentIndex(current_device)

		self.centralwidget = CentralWidget(self.ui.centralwidget, self.logger, "central_widget", 3)
		self.centralLayout = QtGui.QVBoxLayout(self.ui.centralwidget)
		self.centralLayout.setContentsMargins(0, 0, 0, 0)
		self.centralLayout.addWidget(self.centralwidget)

		# this timer is used to update widgets that just need to display as fast as they can
		self.display_timer = QtCore.QTimer()
		self.display_timer.setInterval(SMOOTH_DISPLAY_TIMER_PERIOD_MS) # constant timing

		# timer ticks
		self.connect(self.display_timer, QtCore.SIGNAL('timeout()'), self.update_buffer)
		self.connect(self.display_timer, QtCore.SIGNAL('timeout()'), self.statistics)
		
		# slow timer
		self.slow_timer = QtCore.QTimer()
		self.slow_timer.setInterval(1000) # constant timing

		# timer ticks
		self.connect(self.slow_timer, QtCore.SIGNAL('timeout()'), self.get_cpu_percent)
		
		# toolbar clicks
		self.connect(self.ui.actionStart, QtCore.SIGNAL('triggered()'), self.timer_toggle)
		self.connect(self.ui.actionSettings, QtCore.SIGNAL('triggered()'), self.settings_called)
		self.connect(self.ui.actionAbout, QtCore.SIGNAL('triggered()'), self.about_called)
		self.connect(self.ui.actionNew_dock, QtCore.SIGNAL('triggered()'), self.new_dock_called)
		
		# settings signals
		self.connect(self.settings_dialog.comboBox_inputDevice, QtCore.SIGNAL('currentIndexChanged(int)'), self.input_device_changed)

		# log change
		self.connect(self.logger, QtCore.SIGNAL('logChanged'), self.log_changed)
		self.connect(self.ui.scrollArea_2.verticalScrollBar(), QtCore.SIGNAL('rangeChanged(int,int)'), self.log_scroll_range_changed)
		
		# restore the settings and widgets geometries
		self.restoreAppState()

		# start timers
		self.timer_toggle()
		self.slow_timer.start()
		
		self.logger.push("Init finished, entering the main loop")
	
	# slot
	# update the log widget with the new log content
	def log_changed(self):
		self.ui.LabelLog.setText(self.logger.text())
	
	# slot
	# scroll the log widget so that the last line is visible
	def log_scroll_range_changed(self, min, max):
		scrollbar = self.ui.scrollArea_2.verticalScrollBar()
		scrollbar.setValue(max)
	
	# slot
	def settings_called(self):
		self.settings_dialog.show()
	
	# slot
	def about_called(self):
		self.about_dialog.show()
	
	# slot
	def new_dock_called(self):
		# FIXME the dock objectName should be unique
		index = len(self.docks)
		name = "Dock %d" %index
		new_dock = Dock(self, self.logger, name)
		self.addDockWidget(QtCore.Qt.TopDockWidgetArea, new_dock)
		
		self.docks += [new_dock]
	
	# event handler
	def closeEvent(self, event):
		self.saveAppState()
		event.accept()
	
	# method
	def saveAppState(self):
		settings = QtCore.QSettings("Friture", "Friture")
		
		settings.beginGroup("Docks")
		docknames = [dock.objectName() for dock in self.docks]
		settings.setValue("dockNames", docknames)
		for dock in self.docks:
			settings.beginGroup(dock.objectName())
			dock.saveState(settings)
			settings.endGroup()
		settings.endGroup()
		
		settings.beginGroup("CentralWidget")
		self.centralwidget.saveState(settings)
		settings.endGroup()
		
		settings.beginGroup("MainWindow")
		windowGeometry = self.saveGeometry()
		settings.setValue("windowGeometry", windowGeometry)
		windowState = self.saveState()
		settings.setValue("windowState", windowState)
		settings.endGroup()
	
	# method
	def restoreAppState(self):
		settings = QtCore.QSettings("Friture", "Friture")

		settings.beginGroup("Docks")
		if settings.contains("dockNames"):
			docknames = settings.value("dockNames", []).toList()
			docknames = [dockname.toString() for dockname in docknames]
			# list of docks
			self.docks = [Dock(self, self.logger, name) for name in docknames]
			for dock in self.docks:
				settings.beginGroup(dock.objectName())
				dock.restoreState(settings)
				settings.endGroup()
		else:
			self.logger.push("First launch, display a default set of docks")
			default_docknames = ["Dock 0, Dock 1, Dock 2"]
			self.docks = []
			self.docks += [Dock(self, self.logger, "Dock 0", type = 0)] #level
			self.docks += [Dock(self, self.logger, "Dock 1", type = 1)] #scope
			self.docks += [Dock(self, self.logger, "Dock 2", type = 2)] #spectrum
			for dock in self.docks:
				self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock)
			# by default, hide the log and statistics docks
			self.ui.dockWidgetLog.hide()
			self.ui.dockWidgetStatistics.hide()

		settings.endGroup()

		settings.beginGroup("CentralWidget")
		self.centralwidget.restoreState(settings)
		settings.endGroup()

		settings.beginGroup("MainWindow")
		self.restoreGeometry(settings.value("windowGeometry").toByteArray())
		self.restoreState(settings.value("windowState").toByteArray())
		settings.endGroup()

	# slot
	def timer_toggle(self):
		if self.display_timer.isActive():
			self.logger.push("Timer stop")
			self.display_timer.stop()
		else:
			self.logger.push("Timer start")
			self.display_timer.start()

	# slot
	def update_buffer(self):
		(chunks, t) = self.audiobuffer.update(self.audiobackend.stream)
		self.chunk_number += chunks
		self.buffer_timer_time = (95.*self.buffer_timer_time + 5.*t)/100.

	def get_cpu_percent(self):
		self.cpu_percent = psutil.cpu_percent()

	# method
	def statistics(self):
		if not self.ui.LabelLevel.isVisible():
		    return
		    
		level_label = "Chunk #%d\n"\
		"FFT period : %.01f ms\n"\
		"Spectrogram timer period : %.01f ms\n"\
		"Spectrogram computation: %.02f ms\n"\
		"Audio buffer retrieval: %.02f ms\n"\
		"Levels painting: %.02f ms and %.02f ms\n"\
		"Scope painting: %.02f ms\n"\
		"Spectrum painting: %.02f ms\n"\
		"Spectrogram painting: %.02f ms\n"\
		"Global CPU usage: %d %%"\
		% (self.chunk_number,
		0,#self.ui.spectrum.fft_size*1000./SAMPLING_RATE,
		0,#self.ui.spectrogram.period_ms,
		0,#self.ui.spectrogram.spectrogram_timer_time,
		self.buffer_timer_time,
		0,#self.ui.levels.meter.m_ppValues[0].paint_time,
		0,#self.ui.levels.meter.m_ppValues[1].paint_time,
		0,#self.ui.scope.PlotZoneUp.paint_time,
		0,#self.ui.spectrum.PlotZoneSpect.paint_time,
		0,#self.ui.spectrogram.PlotZoneImage.paint_time)
		self.cpu_percent)
		
		self.ui.LabelLevel.setText(level_label)

	# slot
	def input_device_changed(self, index):
		self.display_timer.stop()
		self.ui.actionStart.setChecked(False)
		
		success, index = self.audiobackend.select_input_device(index)
		
		self.settings_dialog.comboBox_inputDevice.setCurrentIndex(index)
		
		if not success:
			error_message = QtGui.QErrorMessage(self)
			error_message.setWindowTitle("Input device error")
			error_message.showMessage("Impossible to use the selected device, reverting to the previous one")
		
		self.display_timer.start()
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
		try:
			ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
		except:
			print "Could not set the app model ID. If the plaftorm is older than Windows 7, this is normal."

	app = QtGui.QApplication(sys.argv)

	# Splash screen
	pixmap = QtGui.QPixmap(":/splash.png")
	splash = QtGui.QSplashScreen(pixmap)
	splash.show()
	splash.showMessage("Initializing the audio subsystem")
	app.processEvents()
	
	# Set the separator stylesheet here
	# As of Qt 4.6, separator width is not handled correctly
	# when the stylesheet is applied directly to the QMainWindow instance.
	# QtCreator workarounds it with a "minisplitter" special class
	app.setStyleSheet(STYLESHEET)
	
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
