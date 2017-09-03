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
import os
import os.path
import platform
from PyQt5 import QtCore
# specifically import from PyQt5.QtGui and QWidgets for startup time improvement :
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
# importing friture.exceptionhandler also installs a temporary exception hook
from friture.exceptionhandler import errorBox, fileexcepthook
from friture.ui_friture import Ui_MainWindow
from friture.about import About_Dialog  # About dialog
from friture.settings import Settings_Dialog  # Setting dialog
from friture.logger import Logger  # Logging class
from friture.audiobuffer import AudioBuffer  # audio ring buffer class
from friture.audiobackend import AudioBackend  # audio backend class
from friture.centralwidget import CentralWidget
from friture.dockmanager import DockManager
from friture.tilelayout import TileLayout
from friture.levels import Levels_Widget

# the display timer could be made faster when the processing
# power allows it, firing down to every 10 ms
SMOOTH_DISPLAY_TIMER_PERIOD_MS = 10

# the slow timer is used for text refresh
# Text has to be refreshed slowly in order to be readable.
# (and text painting is costly)
SLOW_TIMER_PERIOD_MS = 1000

class Friture(QMainWindow, ):

    def __init__(self):
        QMainWindow.__init__(self)

        # exception hook that logs to console, file, and display a message box
        self.errorDialogOpened = False
        sys.excepthook = self.excepthook

        # Setup the user interface
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize the audio data ring buffer
        self.audiobuffer = AudioBuffer()

        # Initialize the audio backend
        # signal containing new data from the audio callback thread, processed as numpy array
        AudioBackend().new_data_available.connect(self.audiobuffer.handle_new_data)

        # this timer is used to update widgets that just need to display as fast as they can
        self.display_timer = QtCore.QTimer()
        self.display_timer.setInterval(SMOOTH_DISPLAY_TIMER_PERIOD_MS)  # constant timing

        # slow timer
        self.slow_timer = QtCore.QTimer()
        self.slow_timer.setInterval(SLOW_TIMER_PERIOD_MS)  # constant timing

        self.about_dialog = About_Dialog(self, self.slow_timer)
        self.settings_dialog = Settings_Dialog(self)

        self.level_widget = Levels_Widget(self)
        self.level_widget.set_buffer(self.audiobuffer)
        self.audiobuffer.new_data_available.connect(self.level_widget.handle_new_data)

        self.hboxLayout = QHBoxLayout(self.ui.centralwidget)
        self.hboxLayout.setContentsMargins(0, 0, 0, 0)
        self.hboxLayout.addWidget(self.level_widget)

        self.centralLayout = TileLayout()
        self.centralLayout.setContentsMargins(0, 0, 0, 0)

        self.centralwidget = CentralWidget(self.ui.centralwidget, "central_widget")
        self.centralLayout.addWidget(self.centralwidget)

        self.hboxLayout.addLayout(self.centralLayout)

        self.dockmanager = DockManager(self)

        # timer ticks
        self.display_timer.timeout.connect(self.centralwidget.canvasUpdate)
        self.display_timer.timeout.connect(self.dockmanager.canvasUpdate)
        self.display_timer.timeout.connect(self.level_widget.canvasUpdate)

        # toolbar clicks
        self.ui.actionStart.triggered.connect(self.timer_toggle)
        self.ui.actionSettings.triggered.connect(self.settings_called)
        self.ui.actionAbout.triggered.connect(self.about_called)
        self.ui.actionNew_dock.triggered.connect(self.dockmanager.new_dock)

        # restore the settings and widgets geometries
        self.restoreAppState()

        # start timers
        self.timer_toggle()
        self.slow_timer.start()

        Logger().push("Init finished, entering the main loop")

    # exception hook that logs to console, file, and display a message box
    def excepthook(self, exception_type, exception_value, traceback_object):
        gui_message = fileexcepthook(exception_type, exception_value, traceback_object)

        # we do not want to flood the user with message boxes when the error happens repeatedly on each timer event
        if not self.errorDialogOpened:
            self.errorDialogOpened = True
            errorBox(gui_message)
            self.errorDialogOpened = False

    # slot
    def settings_called(self):
        self.settings_dialog.show()

    # slot
    def about_called(self):
        self.about_dialog.show()

    # event handler
    def closeEvent(self, event):
        AudioBackend().close()
        self.saveAppState()
        event.accept()

    # method
    def saveAppState(self):
        settings = QtCore.QSettings("Friture", "Friture")

        settings.beginGroup("Docks")
        self.dockmanager.saveState(settings)
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
        self.dockmanager.restoreState(settings)
        settings.endGroup()

        settings.beginGroup("CentralWidget")
        self.centralwidget.restoreState(settings)
        settings.endGroup()

        settings.beginGroup("MainWindow")
        self.restoreGeometry(settings.value("windowGeometry", type=QtCore.QByteArray))
        self.restoreState(settings.value("windowState", type=QtCore.QByteArray))
        settings.endGroup()

        settings.beginGroup("AudioBackend")
        self.settings_dialog.restoreState(settings)
        settings.endGroup()

    # slot
    def timer_toggle(self):
        if self.display_timer.isActive():
            Logger().push("Timer stop")
            self.display_timer.stop()
            self.ui.actionStart.setText("Start")
            AudioBackend().pause()
            self.centralwidget.pause()
            self.dockmanager.pause()
        else:
            Logger().push("Timer start")
            self.display_timer.start()
            self.ui.actionStart.setText("Stop")
            AudioBackend().restart()
            self.centralwidget.restart()
            self.dockmanager.restart()

def main():
    print("Platform is %s (%s)" %(platform.system(), sys.platform))

    if platform.system() == "Windows":
        print("Applying Windows-specific setup")
        # On Windows, redirect stderr to a file
        import imp
        import ctypes
        if (hasattr(sys, "frozen") or  # new py2exe
                hasattr(sys, "importers") or  # old py2exe
                imp.is_frozen("__main__")):  # tools/freeze
            sys.stderr = open(os.path.expanduser("~/friture.exe.log"), "w")
        # set the App ID for Windows 7 to properly display the icon in the
        # taskbar.
        myappid = 'Friture.Friture.Friture.current'  # arbitrary string
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            print("Could not set the app model ID. If the plaftorm is older than Windows 7, this is normal.")

    app = QApplication(sys.argv)

    if platform.system() == "Darwin":
        if hasattr(sys, "frozen"): #py2app
            sys.stdout = open(os.path.expanduser("~/friture.out.txt"), "w")
            sys.stderr = open(os.path.expanduser("~/friture.err.txt"), "w")

        print("Applying Mac OS-specific setup")
        # help the py2app-packaged application find the Qt plugins (imageformats and platforms)
        pluginsPath = os.path.normpath(os.path.join(QApplication.applicationDirPath(), os.path.pardir, 'PlugIns'))
        print("Adding the following to the Library paths: " + pluginsPath)
        QApplication.addLibraryPath(pluginsPath)

    # Splash screen
    pixmap = QPixmap(":/images/splash.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    splash.showMessage("Initializing the audio subsystem")
    app.processEvents()

    window = Friture()
    window.show()
    splash.finish(window)

    profile = "no"  # "python" or "kcachegrind" or anything else to disable

    if len(sys.argv) > 1:
        if sys.argv[1] == "--python":
            profile = "python"
        elif sys.argv[1] == "--kcachegrind":
            profile = "kcachegrind"
        elif sys.argv[1] == "--no":
            profile = "no"
        else:
            print("command-line arguments (%s) not recognized" % sys.argv[1:])

    if profile == "python":
        import cProfile
        import pstats

        cProfile.runctx('app.exec_()', globals(), locals(), filename="friture.cprof")

        stats = pstats.Stats("friture.cprof")
        stats.strip_dirs().sort_stats('time').print_stats(20)
        stats.strip_dirs().sort_stats('cumulative').print_stats(20)

        sys.exit(0)
    elif profile == "kcachegrind":
        import cProfile
        import lsprofcalltree

        p = cProfile.Profile()
        p.run('app.exec_()')

        k = lsprofcalltree.KCacheGrind(p)
        with open('cachegrind.out.00000', 'wb') as data:
            k.output(data)

        sys.exit(0)
    else:
        sys.exit(app.exec_())
