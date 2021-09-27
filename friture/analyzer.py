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
import errno
import platform
import logging
import logging.handlers

from PyQt5 import QtCore
# specifically import from PyQt5.QtGui and QWidgets for startup time improvement :
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtQml import QQmlEngine, qmlRegisterSingletonType, qmlRegisterType
import appdirs

# importing friture.exceptionhandler also installs a temporary exception hook
from friture.exceptionhandler import errorBox, fileexcepthook
import friture
from friture.ui_friture import Ui_MainWindow
from friture.about import About_Dialog  # About dialog
from friture.settings import Settings_Dialog  # Setting dialog
from friture.audiobuffer import AudioBuffer  # audio ring buffer class
from friture.audiobackend import AudioBackend  # audio backend class
from friture.dockmanager import DockManager
from friture.tilelayout import TileLayout
from friture.level_view_model import LevelViewModel
from friture.level_data import LevelData
from friture.levels import Levels_Widget
from friture.store import GetStore, Store
from friture.scope_data import Scope_Data
from friture.axis import Axis
from friture.curve import Curve
from friture.plotCurve import PlotCurve
from friture.plotting.coordinateTransform import CoordinateTransform
from friture.plotting.scaleDivision import ScaleDivision, Tick
from friture.spectrum_data import Spectrum_Data
from friture.plotFilledCurve import PlotFilledCurve
from friture.filled_curve import FilledCurve
from friture.qml_tools import qml_url

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

        self.logger = logging.getLogger(__name__)        

        # exception hook that logs to console, file, and display a message box
        self.errorDialogOpened = False
        sys.excepthook = self.excepthook
        
        store = GetStore()

        # set the store as the parent of the QML engine
        # so that the store outlives the engine
        # otherwise the store gets destroyed before the engine
        # which refreshes the QML bindings to undefined values
        # and QML errors are raised
        self.qml_engine = QQmlEngine(store)

        # Register the ScaleDivision type.  Its URI is 'ScaleDivision', it's v1.0 and the type
        # will be called 'Person' in QML.
        qmlRegisterType(ScaleDivision, 'Friture', 1, 0, 'ScaleDivision')
        qmlRegisterType(CoordinateTransform, 'Friture', 1, 0, 'CoordinateTransform')
        qmlRegisterType(Scope_Data, 'Friture', 1, 0, 'ScopeData')
        qmlRegisterType(Spectrum_Data, 'Friture', 1, 0, 'SpectrumData')
        qmlRegisterType(LevelData, 'Friture', 1, 0, 'LevelData')
        qmlRegisterType(LevelViewModel, 'Friture', 1, 0, 'LevelViewModel')
        qmlRegisterType(Axis, 'Friture', 1, 0, 'Axis')
        qmlRegisterType(Curve, 'Friture', 1, 0, 'Curve')
        qmlRegisterType(FilledCurve, 'Friture', 1, 0, 'FilledCurve')
        qmlRegisterType(PlotCurve, 'Friture', 1, 0, 'PlotCurve')
        qmlRegisterType(PlotFilledCurve, 'Friture', 1, 0, 'PlotFilledCurve')
        qmlRegisterType(Tick, 'Friture', 1, 0, 'Tick')
        qmlRegisterSingletonType(Store, 'Friture', 1, 0, 'Store', lambda engine, script_engine: GetStore())

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

        self.level_widget = Levels_Widget(self, self.qml_engine)
        self.level_widget.set_buffer(self.audiobuffer)
        self.audiobuffer.new_data_available.connect(self.level_widget.handle_new_data)

        self.hboxLayout = QHBoxLayout(self.ui.centralwidget)
        self.hboxLayout.setContentsMargins(0, 0, 0, 0)
        self.hboxLayout.addWidget(self.level_widget)

        self.centralLayout = TileLayout()
        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.hboxLayout.addLayout(self.centralLayout)

        self.dockmanager = DockManager(self)

        # timer ticks
        self.display_timer.timeout.connect(self.dockmanager.canvasUpdate)
        self.display_timer.timeout.connect(self.level_widget.canvasUpdate)
        self.display_timer.timeout.connect(AudioBackend().fetchAudioData)

        # toolbar clicks
        self.ui.actionStart.triggered.connect(self.timer_toggle)
        self.ui.actionSettings.triggered.connect(self.settings_called)
        self.ui.actionAbout.triggered.connect(self.about_called)
        self.ui.actionNew_dock.triggered.connect(self.dockmanager.new_dock)

        # restore the settings and widgets geometries
        self.restoreAppState()

        # make sure the toolbar is shown
        # in case it was closed by mistake (before it was made impossible)
        self.ui.toolBar.setVisible(True)

        # prevent from hiding or moving the toolbar
        self.ui.toolBar.toggleViewAction().setVisible(False)
        self.ui.toolBar.setMovable(False)
        self.ui.toolBar.setFloatable(False)

        # start timers
        self.timer_toggle()
        self.slow_timer.start()

        self.logger.info("Init finished, entering the main loop")

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
    def migrateSettings(self):
        settings = QtCore.QSettings("Friture", "Friture")

        # 1. move the central widget to a normal dock
        if settings.contains("CentralWidget/type"):
            settings.beginGroup("CentralWidget")
            centralWidgetKeys = settings.allKeys()
            children = {key: settings.value(key, type=QtCore.QVariant) for key in centralWidgetKeys}
            settings.endGroup()

            if not settings.contains("Docks/central/type"):
                # write them to a new dock instead
                for key, value in children.items():
                    settings.setValue("Docks/central/" + key, value)

                # add the new dock name to dockNames
                docknames = settings.value("Docks/dockNames", [])
                docknames = ["central"] + docknames
                settings.setValue("Docks/dockNames", docknames)

            settings.remove("CentralWidget")

        # 2. remove any level widget
        if settings.contains("Docks/dockNames"):
            docknames = settings.value("Docks/dockNames", [])
            if docknames == None:
            	docknames = []
            newDockNames = []
            for dockname in docknames:
                widgetType = settings.value("Docks/" + dockname + "/type", 0, type=int)
                if widgetType == 0:
                    settings.remove("Docks/" + dockname)
                else:
                    newDockNames.append(dockname)
            settings.setValue("Docks/dockNames", newDockNames)

    # method
    def restoreAppState(self):
        self.migrateSettings()

        settings = QtCore.QSettings("Friture", "Friture")

        settings.beginGroup("Docks")
        self.dockmanager.restoreState(settings)
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
            self.logger.info("Timer stop")
            self.display_timer.stop()
            self.ui.actionStart.setText("Start")
            AudioBackend().pause()
            self.dockmanager.pause()
        else:
            self.logger.info("Timer start")
            self.display_timer.start()
            self.ui.actionStart.setText("Stop")
            AudioBackend().restart()
            self.dockmanager.restart()


def qt_message_handler(mode, context, message):
    logger = logging.getLogger(__name__)
    if mode == QtCore.QtInfoMsg:
        logger.info(message)
    elif mode == QtCore.QtWarningMsg:
        logger.warning(message)
    elif mode == QtCore.QtCriticalMsg:
        logger.error(message)
    elif mode == QtCore.QtFatalMsg:
        logger.critical(message)
    else:
        logger.debug(message)


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def main():
    # make the Python warnings go to Friture logger
    logging.captureWarnings(True)

    logFormat = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    formatter = logging.Formatter(logFormat)

    logFileName = "friture.log.txt"
    dirs = appdirs.AppDirs("Friture", "")
    logDir = dirs.user_data_dir
    try:
        os.makedirs(logDir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    logFilePath = os.path.join(logDir, logFileName)

    # log to file
    fileHandler = logging.handlers.RotatingFileHandler(logFilePath, maxBytes=100000, backupCount=5)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)
    rootLogger.addHandler(fileHandler)

    if hasattr(sys, "frozen"):
        # redirect stdout and stderr to the logger if this is a pyinstaller bundle
        sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
        sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.ERROR)
    else:
        # log to console if this is not a pyinstaller bundle
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)
        rootLogger.addHandler(console)

    # make Qt logs go to Friture logger
    QtCore.qInstallMessageHandler(qt_message_handler)

    logger = logging.getLogger(__name__)

    logger.info("Friture %s starting on %s (%s)", friture.__version__, platform.system(), sys.platform)

    logger.info("QML path: %s", qml_url(""))

    if platform.system() == "Windows":
        logger.info("Applying Windows-specific setup")

        # enable automatic scaling for high-DPI screens
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        # set the App ID for Windows 7 to properly display the icon in the
        # taskbar.
        import ctypes
        myappid = 'Friture.Friture.Friture.current'  # arbitrary string
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            logger.error("Could not set the app model ID. If the plaftorm is older than Windows 7, this is normal.")

    app = QApplication(sys.argv)

    if platform.system() == "Darwin":
        logger.info("Applying Mac OS-specific setup")
        # help the packaged application find the Qt plugins (imageformats and platforms)
        pluginsPath = os.path.normpath(os.path.join(QApplication.applicationDirPath(), os.path.pardir, 'PlugIns'))
        logger.info("Adding the following to the Library paths: %s", pluginsPath)
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
            logger.info("command-line arguments (%s) not recognized", sys.argv[1:])

    return_code = 0
    if profile == "python":
        import cProfile
        import pstats

        # friture.cprof can be visualized with SnakeViz
        # http://jiffyclub.github.io/snakeviz/
        # snakeviz friture.cprof
        cProfile.runctx('app.exec_()', globals(), locals(), filename="friture.cprof")

        logger.info("Profile saved to '%s'", "friture.cprof")

        stats = pstats.Stats("friture.cprof")
        stats.strip_dirs().sort_stats('time').print_stats(20)
        stats.strip_dirs().sort_stats('cumulative').print_stats(20)
    elif profile == "kcachegrind":
        import cProfile
        import lsprofcalltree

        p = cProfile.Profile()
        p.run('app.exec_()')

        k = lsprofcalltree.KCacheGrind(p)
        with open('cachegrind.out.00000', 'wb') as data:
            k.output(data)
    else:
        return_code = app.exec_()

    # explicitly delete the main windows instead of waiting for the interpreter shutdown
    # tentative to prevent errors on exit on macos
    del window

    sys.exit(return_code)
