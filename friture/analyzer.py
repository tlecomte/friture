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
from friture.defaults import DEFAULT_DOCKS
import psutil # for CPU usage monitoring

# the display timer could be made faster when the processing
# power allows it, firing down to every 10 ms
SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25

# the slow timer is used for text refresh
# Text has to be refreshed slowly in order to be readable.
# (and text painting is costly)
SLOW_TIMER_PERIOD_MS = 1000

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
		
		self.chunk_number = 0
		
		self.buffer_timer_time = 0.
		
		self.cpu_percent = 0.

		# Initialize the audio data ring buffer
		self.audiobuffer = AudioBuffer(self.logger)

		# Initialize the audio backend
		self.audiobackend = AudioBackend(self.logger)

		self.about_dialog = About_Dialog(self)
		self.settings_dialog = Settings_Dialog(self, self.logger, self.audiobackend)

		# this timer is used to update widgets that just need to display as fast as they can
		self.display_timer = QtCore.QTimer()
		self.display_timer.setInterval(SMOOTH_DISPLAY_TIMER_PERIOD_MS) # constant timing

		# slow timer
		self.slow_timer = QtCore.QTimer()
		self.slow_timer.setInterval(SLOW_TIMER_PERIOD_MS) # constant timing

		self.centralwidget = CentralWidget(self.ui.centralwidget, self.logger, "central_widget", 0)
		self.centralLayout = QVBoxLayout(self.ui.centralwidget)
		self.centralLayout.setContentsMargins(0, 0, 0, 0)
		self.centralLayout.addWidget(self.centralwidget)

		# timer ticks
		self.connect(self.display_timer, QtCore.SIGNAL('timeout()'), self.update_buffer)
		self.connect(self.display_timer, QtCore.SIGNAL('timeout()'), self.centralwidget.update)

		# timer ticks
		self.connect(self.slow_timer, QtCore.SIGNAL('timeout()'), self.get_cpu_percent)
		self.connect(self.slow_timer, QtCore.SIGNAL('timeout()'), self.statistics)

		# toolbar clicks
		self.connect(self.ui.actionStart, QtCore.SIGNAL('triggered()'), self.timer_toggle)
		self.connect(self.ui.actionSettings, QtCore.SIGNAL('triggered()'), self.settings_called)
		self.connect(self.ui.actionAbout, QtCore.SIGNAL('triggered()'), self.about_called)
		self.connect(self.ui.actionNew_dock, QtCore.SIGNAL('triggered()'), self.new_dock_called)

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
		self.connect(self.display_timer, QtCore.SIGNAL('timeout()'), new_dock.update)
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
			self.docks = [Dock(self, self.logger, "Dock %d" %(i), type = type) for i, type in enumerate(DEFAULT_DOCKS)]
			for dock in self.docks:
				self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock)

		for dock in self.docks:
			self.connect(self.display_timer, QtCore.SIGNAL('timeout()'), dock.update)

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
		else:
			self.logger.push("Timer start")
			self.display_timer.start()
			self.ui.actionStart.setText("Stop")

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
		"Global CPU usage: %d %%\n"\
		"Number of overflowed inputs (XRUNs): %d"\
		% (self.chunk_number, self.buffer_timer_time, self.cpu_percent, self.audiobackend.xruns)
		
		self.about_dialog.LabelStats.setText(label)


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
