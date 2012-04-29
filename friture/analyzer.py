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
from PyQt4 import QtCore
# specifically import from PyQt4.QtGui for startup time improvement :
from PyQt4.QtGui import QMainWindow, QVBoxLayout, QErrorMessage, QApplication, QPixmap, QSplashScreen
from friture.ui_friture import Ui_MainWindow
from friture.dock import Dock
from friture.about import About_Dialog # About dialog
from friture.settings import Settings_Dialog # Setting dialog
from friture.logger import Logger # Logging class
from friture.audiobuffer import AudioBuffer # audio ring buffer class
from friture.audiobackend import AudioBackend# audio backend class
from friture.centralwidget import CentralWidget
import psutil # for CPU usage monitoring

# the sample rate below should be dynamic, taken from PyAudio/PortAudio
SAMPLING_RATE = 44100

# the display timer could be made faster when the processing
# power allows it, firing down to every 10 ms
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

class Friture(QMainWindow, ):
	def __init__(self, logger):
		QMainWindow.__init__(self)

		# logger
		self.logger = logger

		# Setup the user interface
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		
		self.settings_dialog = Settings_Dialog(self)
		self.about_dialog = About_Dialog(self)
		
		self.chunk_number = 0
		
		self.buffer_timer_time = 0.
		
		self.cpu_percent = 0.

		# Initialize the audio data ring buffer
		self.audiobuffer = AudioBuffer()

		# Initialize the audio backend
		self.audiobackend = AudioBackend(self.logger)
   
		devices = self.audiobackend.get_readable_devices_list()
		for device in devices:
			self.settings_dialog.comboBox_inputDevice.addItem(device)

		channels = self.audiobackend.get_readable_current_channels()
		for channel in channels:
			self.settings_dialog.comboBox_firstChannel.addItem(channel)
			self.settings_dialog.comboBox_secondChannel.addItem(channel)

		current_device = self.audiobackend.get_readable_current_device()
		self.settings_dialog.comboBox_inputDevice.setCurrentIndex(current_device)

		first_channel = self.audiobackend.get_current_first_channel()
		self.settings_dialog.comboBox_firstChannel.setCurrentIndex(first_channel)
		second_channel = self.audiobackend.get_current_second_channel()
		self.settings_dialog.comboBox_secondChannel.setCurrentIndex(second_channel)

		# this timer is used to update widgets that just need to display as fast as they can
		self.display_timer = QtCore.QTimer()
		self.display_timer.setInterval(SMOOTH_DISPLAY_TIMER_PERIOD_MS) # constant timing

		# slow timer
		self.slow_timer = QtCore.QTimer()
		self.slow_timer.setInterval(1000) # constant timing

		self.centralwidget = CentralWidget(self.ui.centralwidget, self.logger, "central_widget", 0)
		self.centralLayout = QVBoxLayout(self.ui.centralwidget)
		self.centralLayout.setContentsMargins(0, 0, 0, 0)
		self.centralLayout.addWidget(self.centralwidget)

		# timer ticks
		self.connect(self.display_timer, QtCore.SIGNAL('timeout()'), self.update_buffer)
		self.connect(self.display_timer, QtCore.SIGNAL('timeout()'), self.statistics)

		# timer ticks
		self.connect(self.slow_timer, QtCore.SIGNAL('timeout()'), self.get_cpu_percent)
		
		# toolbar clicks
		self.connect(self.ui.actionStart, QtCore.SIGNAL('triggered()'), self.timer_toggle)
		self.connect(self.ui.actionSettings, QtCore.SIGNAL('triggered()'), self.settings_called)
		self.connect(self.ui.actionAbout, QtCore.SIGNAL('triggered()'), self.about_called)
		self.connect(self.ui.actionNew_dock, QtCore.SIGNAL('triggered()'), self.new_dock_called)
		
		# settings signals
		self.connect(self.settings_dialog.comboBox_inputDevice, QtCore.SIGNAL('currentIndexChanged(int)'), self.input_device_changed)
  		self.connect(self.settings_dialog.comboBox_firstChannel, QtCore.SIGNAL('currentIndexChanged(int)'), self.first_channel_changed)
		self.connect(self.settings_dialog.comboBox_secondChannel, QtCore.SIGNAL('currentIndexChanged(int)'), self.second_channel_changed)
		self.connect(self.settings_dialog.radioButton_single, QtCore.SIGNAL('toggled(bool)'), self.single_input_type_selected)
		self.connect(self.settings_dialog.radioButton_duo, QtCore.SIGNAL('toggled(bool)'), self.duo_input_type_selected)
		self.connect(self.settings_dialog.doubleSpinBox_delay, QtCore.SIGNAL('valueChanged(double)'), self.delay_changed)

		# log change
		self.connect(self.logger, QtCore.SIGNAL('logChanged'), self.log_changed)
		self.connect(self.about_dialog.log_scrollarea.verticalScrollBar(), QtCore.SIGNAL('rangeChanged(int,int)'), self.log_scroll_range_changed)

		# restore the settings and widgets geometries
		self.restoreAppState()

		# start timers
		self.timer_toggle()
		self.slow_timer.start()
		
		self.logger.push("Init finished, entering the main loop")
	
	# slot
	# update the log widget with the new log content
	def log_changed(self):
		self.about_dialog.LabelLog.setText(self.logger.text())
	
	# slot
	# scroll the log widget so that the last line is visible
	def log_scroll_range_changed(self, min, max):
		scrollbar = self.about_dialog.log_scrollarea.verticalScrollBar()
		scrollbar.setValue(max)
	
	# slot
	def settings_called(self):
		self.settings_dialog.show()
	
	# slot
	def about_called(self):
		self.about_dialog.show()
	
	# slot
	def new_dock_called(self):
		# the dock objectName is unique
		docknames = [dock.objectName() for dock in self.docks]
		dockindexes = [int(str(name).partition(' ')[-1]) for name in docknames]
		if len(dockindexes) == 0:
			index = 1
		else:
			index = max(dockindexes)+1
		name = "Dock %d" %index
		new_dock = Dock(self, self.logger, name)
		self.addDockWidget(QtCore.Qt.TopDockWidgetArea, new_dock)
		
		self.docks += [new_dock]
	
	#slot
	def dock_closed(self, dock):
		self.docks.remove(dock)
		dock.deleteLater()
	
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

		settings.beginGroup("AudioBackend")
		self.settings_dialog.saveState(settings)
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
			self.docks = []
			self.docks += [Dock(self, self.logger, "Dock 0", type = 3)] #spectrogram
			self.docks += [Dock(self, self.logger, "Dock 1", type = 4)] #octave spectrum
			#self.docks += [Dock(self, self.logger, "Dock 2", type = 1)] #scope
			#self.docks += [Dock(self, self.logger, "Dock 3", type = 0)] #level
			for dock in self.docks:
				self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock)

		settings.endGroup()

		settings.beginGroup("CentralWidget")
		self.centralwidget.restoreState(settings)
		settings.endGroup()

		settings.beginGroup("MainWindow")
		self.restoreGeometry(settings.value("windowGeometry").toByteArray())
		self.restoreState(settings.value("windowState").toByteArray())
		settings.endGroup()
  
  		settings.beginGroup("AudioBackend")
		self.settings_dialog.restoreState(settings)
		settings.endGroup()

	# slot
	def timer_toggle(self):
		if self.display_timer.isActive():
			self.logger.push("Timer stop")
			self.display_timer.stop()
			self.ui.actionStart.setText("Start")
			for dock in self.docks:
				dock.custom_timer_stop()
			self.centralwidget.custom_timer_stop()
		else:
			self.logger.push("Timer start")
			self.display_timer.start()
			self.ui.actionStart.setText("Stop")
			for dock in self.docks:
				dock.custom_timer_start()
			self.centralwidget.custom_timer_start()

	# slot
	def update_buffer(self):
     		(chunks, t, newpoints) = self.audiobackend.update(self.audiobuffer.ringbuffer)
     		self.audiobuffer.set_newdata(newpoints)
		self.chunk_number += chunks
		self.buffer_timer_time = (95.*self.buffer_timer_time + 5.*t)/100.

	def get_cpu_percent(self):
		self.cpu_percent = psutil.cpu_percent(0)

	# method
	def statistics(self):
		if not self.about_dialog.LabelStats.isVisible():
		    return
		    
		label = "Chunk #%d\n"\
		"Audio buffer retrieval: %.02f ms\n"\
		"Global CPU usage: %d %%"\
		% (self.chunk_number, self.buffer_timer_time, self.cpu_percent)
		
		self.about_dialog.LabelStats.setText(label)

	# slot
	def input_device_changed(self, index):
		self.ui.actionStart.setChecked(False)
		
		success, index = self.audiobackend.select_input_device(index)
		
		self.settings_dialog.comboBox_inputDevice.setCurrentIndex(index)
		
		if not success:
			# Note: the error message is a child of the settings dialog, so that
			# that dialog remains on top when the error message is closed
			error_message = QErrorMessage(self.settings_dialog)
			error_message.setWindowTitle("Input device error")
			error_message.showMessage("Impossible to use the selected input device, reverting to the previous one")
		
		# reset the channels
		first_channel = self.audiobackend.get_current_first_channel()
		self.settings_dialog.comboBox_firstChannel.setCurrentIndex(first_channel)
		second_channel = self.audiobackend.get_current_second_channel()
		self.settings_dialog.comboBox_secondChannel.setCurrentIndex(second_channel)  
  
		self.ui.actionStart.setChecked(True)

	# slot
	def first_channel_changed(self, index):
		self.ui.actionStart.setChecked(False)
		
		success, index = self.audiobackend.select_first_channel(index)
		
		self.settings_dialog.comboBox_firstChannel.setCurrentIndex(index)
		
		if not success:
			# Note: the error message is a child of the settings dialog, so that
			# that dialog remains on top when the error message is closed
			error_message = QErrorMessage(self.settings_dialog)
			error_message.setWindowTitle("Input device error")
			error_message.showMessage("Impossible to use the selected channel as the first channel, reverting to the previous one")
		
		self.ui.actionStart.setChecked(True)

	# slot
	def second_channel_changed(self, index):
		self.ui.actionStart.setChecked(False)
		
		success, index = self.audiobackend.select_second_channel(index)
		
		self.settings_dialog.comboBox_secondChannel.setCurrentIndex(index)
		
		if not success:
			# Note: the error message is a child of the settings dialog, so that
			# that dialog remains on top when the error message is closed
			error_message = QErrorMessage(self.settings_dialog)
			error_message.setWindowTitle("Input device error")
			error_message.showMessage("Impossible to use the selected channel as the second channel, reverting to the previous one")
		
		self.ui.actionStart.setChecked(True)

	# slot
	def single_input_type_selected(self, checked):
                if checked:
                    self.settings_dialog.groupBox_second.setEnabled(False)
                    self.settings_dialog.label_delay.setEnabled(False)
                    self.settings_dialog.doubleSpinBox_delay.setEnabled(False)
                    self.audiobackend.set_single_input()
                    self.logger.push("Switching to single input")

	# slot
	def duo_input_type_selected(self, checked):
                if checked:
                    self.settings_dialog.groupBox_second.setEnabled(True)
                    self.settings_dialog.label_delay.setEnabled(True)
                    self.settings_dialog.doubleSpinBox_delay.setEnabled(True)
                    self.audiobackend.set_duo_input()
                    self.logger.push("Switching to difference between two inputs")

	# slot
	def delay_changed(self, delay_ms):
                    self.delay_ms = delay_ms
                    self.logger.push("Delay changed to %f" %delay_ms)
                    self.audiobuffer.set_delay_ms(delay_ms)

def main():
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

	app = QApplication(sys.argv)

	# Splash screen
	pixmap = QPixmap(":/images/splash.png")
	splash = QSplashScreen(pixmap)
	splash.show()
	splash.showMessage("Initializing the audio subsystem")
	app.processEvents()
	
	# Set the separator stylesheet here
	# As of Qt 4.6, separator width is not handled correctly
	# when the stylesheet is applied directly to the QMainWindow instance.
	# QtCreator workarounds it with a "minisplitter" special class
	app.setStyleSheet(STYLESHEET)
	
	# Logger class
	logger = Logger()
	
	window = Friture(logger)
	window.show()
	splash.finish(window)
	
	profile = "no" # "python" or "kcachegrind" or anything else to disable

	if len(sys.argv) > 1:
		if sys.argv[1] == "--python":
			profile = "python"
		#elif sys.argv[1] == "--kcachegrind":
			#profile = "kcachegrind"
		elif sys.argv[1] == "--no":
			profile = "no"
		else:
			print "command-line arguments (%s) not recognized" %sys.argv[1:]

	if profile == "python":
		import cProfile
		import pstats
		
		cProfile.runctx('app.exec_()', globals(), locals(), filename="friture.cprof")
		
		stats = pstats.Stats("friture.cprof")
		stats.strip_dirs().sort_stats('time').print_stats(20)
		stats.strip_dirs().sort_stats('cumulative').print_stats(20)  
  
		sys.exit(0)
	#elif profile == "kcachegrind":
		#import cProfile
		#import lsprofcalltree

		#p = cProfile.Profile()
		#p.run('app.exec_()')
		
		#k = lsprofcalltree.KCacheGrind(p)
		#data = open('cachegrind.out.00000', 'wb')
		#k.output(data)
		#data.close()

		## alternative code with pyprof2calltree instead of lsprofcalltree
		##import pyprof2calltree
		##pyprof2calltree.convert(p.getstats(), "cachegrind.out.00000") # save
		
		#sys.exit(0)
	else:
		sys.exit(app.exec_())
