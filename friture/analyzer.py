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
import argparse
import errno
import platform
import logging
import logging.handlers

from PyQt5 import QtCore
# specifically import from PyQt5.QtGui and QWidgets for startup time improvement :
from PyQt5.QtWidgets import QMainWindow, QApplication, QSplashScreen, QWidget
from PyQt5.QtGui import QPixmap, QFontDatabase
from PyQt5.QtQml import QQmlEngine, qmlRegisterSingletonType, qmlRegisterType
from PyQt5.QtCore import QObject
from PyQt5.QtQuick import QQuickView

import platformdirs

# importing friture.exceptionhandler also installs a temporary exception hook
from friture.exceptionhandler import errorBox, fileexcepthook
import friture
from friture.main_toolbar_view_model import MainToolbarViewModel
from friture.playback.playback_control_view_model import PlaybackControlViewModel
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
from friture.main_window_view_model import MainWindowViewModel
from friture.store import GetStore, Store
from friture.scope_data import Scope_Data
from friture.axis import Axis
from friture.colorBar import ColorBar
from friture.curve import Curve
from friture.playback.control import PlaybackControlWidget
from friture.playback.player import Player
from friture.plotCurve import PlotCurve
from friture.plotting.coordinateTransform import CoordinateTransform
from friture.plotting.scaleDivision import ScaleDivision, Tick
from friture.spectrogram_item import SpectrogramItem
from friture.spectrogram_item_data import SpectrogramImageData
from friture.spectrum_data import Spectrum_Data
from friture.plotFilledCurve import PlotFilledCurve
from friture.filled_curve import FilledCurve
from friture.qml_tools import qml_url, view_raise_if_error
from friture.generators.sine import Sine_Generator_Settings_View_Model
from friture.generators.white import White_Generator_Settings_View_Model
from friture.generators.pink import Pink_Generator_Settings_View_Model
from friture.generators.sweep import Sweep_Generator_Settings_View_Model
from friture.generators.burst import Burst_Generator_Settings_View_Model

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
        qmlRegisterType(PlaybackControlViewModel, 'Friture', 1, 0, 'PlaybackControlViewModel')
        qmlRegisterType(MainWindowViewModel, 'Friture', 1, 0, 'MainWindowViewModel')
        qmlRegisterType(MainToolbarViewModel, 'Friture', 1, 0, 'MainToolbarViewModel')
        qmlRegisterType(Axis, 'Friture', 1, 0, 'Axis')
        qmlRegisterType(Curve, 'Friture', 1, 0, 'Curve')
        qmlRegisterType(FilledCurve, 'Friture', 1, 0, 'FilledCurve')
        qmlRegisterType(PlotCurve, 'Friture', 1, 0, 'PlotCurve')
        qmlRegisterType(PlotFilledCurve, 'Friture', 1, 0, 'PlotFilledCurve')
        qmlRegisterType(SpectrogramItem, 'Friture', 1, 0, 'SpectrogramItem')
        qmlRegisterType(SpectrogramImageData, 'Friture', 1, 0, 'SpectrogramImageData')
        qmlRegisterType(ColorBar, 'Friture', 1, 0, 'ColorBar')
        qmlRegisterType(Tick, 'Friture', 1, 0, 'Tick')
        qmlRegisterType(TileLayout, 'Friture', 1, 0, 'TileLayout')
        qmlRegisterType(Burst_Generator_Settings_View_Model, 'Friture', 1, 0, 'Burst_Generator_Settings_View_Model')
        qmlRegisterType(Pink_Generator_Settings_View_Model, 'Friture', 1, 0, 'Pink_Generator_Settings_View_Model')
        qmlRegisterType(White_Generator_Settings_View_Model, 'Friture', 1, 0, 'White_Generator_Settings_View_Model')
        qmlRegisterType(Sweep_Generator_Settings_View_Model, 'Friture', 1, 0, 'Sweep_Generator_Settings_View_Model')
        qmlRegisterType(Sine_Generator_Settings_View_Model, 'Friture', 1, 0, 'Sine_Generator_Settings_View_Model')

        qmlRegisterSingletonType(Store, 'Friture', 1, 0, 'Store', lambda engine, script_engine: GetStore())

        # Setup the user interface
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize the audio data ring buffer
        self.audiobuffer = AudioBuffer()

        # Initialize the audio backend
        # signal containing new data from the audio callback thread, processed as numpy array
        AudioBackend().new_data_available.connect(self.audiobuffer.handle_new_data)

        self.player = Player(self)
        self.audiobuffer.new_data_available.connect(self.player.handle_new_data)

        # this timer is used to update widgets that just need to display as fast as they can
        self.display_timer = QtCore.QTimer()
        self.display_timer.setInterval(SMOOTH_DISPLAY_TIMER_PERIOD_MS)  # constant timing

        # slow timer
        self.slow_timer = QtCore.QTimer()
        self.slow_timer.setInterval(SLOW_TIMER_PERIOD_MS)  # constant timing

        self._main_window_view_model = MainWindowViewModel(self.qml_engine)

        self.about_dialog = About_Dialog(self, self.slow_timer)
        self.settings_dialog = Settings_Dialog(self, self._main_window_view_model.toolbar_view_model)

        self.quick_view = QQuickView(self.qml_engine, None)
        self.quick_view.setResizeMode(QQuickView.SizeRootObjectToView)
        self.quick_view.setInitialProperties({
            "main_window_view_model": self._main_window_view_model,
            "fixedFont": QFontDatabase.systemFont(QFontDatabase.FixedFont).family()
        })
        self.quick_view.setSource(qml_url("FritureMainWindow.qml"))

        view_raise_if_error(self.quick_view)

        self.quick_container = QWidget.createWindowContainer(self.quick_view, self)
        self.setCentralWidget(self.quick_container)

        self.main_tile_layout = self.quick_view.findChild(QObject, "main_tile_layout")
        assert self.main_tile_layout is not None, "Main tile layout not found in CentralWidget.qml"

        self.level_widget = Levels_Widget(self, self._main_window_view_model.level_view_model)
        self.level_widget.set_buffer(self.audiobuffer)
        self.audiobuffer.new_data_available.connect(self.level_widget.handle_new_data)

        self.playback_widget = PlaybackControlWidget(self, self.player, self._main_window_view_model.playback_control_view_model)

        self.dockmanager = DockManager(self, self.main_tile_layout)

        # timer ticks
        self.display_timer.timeout.connect(self.dockmanager.canvasUpdate)
        self.display_timer.timeout.connect(self.level_widget.canvasUpdate)
        self.display_timer.timeout.connect(AudioBackend().fetchAudioData)

        # toolbar clicks
        self._main_window_view_model.toolbar_view_model.recording_clicked.connect(self.timer_toggle)
        self._main_window_view_model.toolbar_view_model.new_dock_clicked.connect(self.dockmanager.new_dock)
        self._main_window_view_model.toolbar_view_model.settings_clicked.connect(self.settings_called)
        self._main_window_view_model.toolbar_view_model.about_clicked.connect(self.about_called)
        self.playback_widget.recording_toggled.connect(self.timer_changed)

        # settings changes
        self.settings_dialog.show_playback_changed.connect(self.show_playback_changed)
        self.settings_dialog.history_length_changed.connect(self.player.set_history_seconds)

        # restore the settings and widgets geometries
        self.restoreAppState()

        # start timers
        self.timer_toggle()
        self.slow_timer.start()

        self.logger.info("Init finished, entering the main loop")

    # exception hook that logs to console, file, and display a message box
    def excepthook(self, exception_type, exception_value, traceback_object):
        # a keyboard interrupt is an intentional exit, so close the application
        if exception_type is KeyboardInterrupt:
            self.close()
            exit(0)

        gui_message = fileexcepthook(exception_type, exception_value, traceback_object)

        # we do not want to flood the user with message boxes when the error happens repeatedly on each timer event
        if not self.errorDialogOpened:
            self.errorDialogOpened = True
            errorBox(gui_message)
            self.errorDialogOpened = False

    # slot
    def settings_called(self):
        self.settings_dialog.show()

    def show_playback_changed(self, show: bool) -> None:
        self._main_window_view_model.playback_control_enabled = show

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
            self._main_window_view_model.toolbar_view_model.recording = False
            self.playback_widget.stop_recording()
            AudioBackend().pause()
            self.dockmanager.pause()
        else:
            self.logger.info("Timer start")
            self.display_timer.start()
            self._main_window_view_model.toolbar_view_model.recording = True
            self.playback_widget.start_recording()
            AudioBackend().restart()
            self.dockmanager.restart()

    # slot
    def timer_changed(self, recording: bool):
        if not recording and self.display_timer.isActive():
            self.logger.info("Timer stop")
            self.display_timer.stop()
            self._main_window_view_model.toolbar_view_model.recording = False
            self.playback_widget.stop_recording()
            AudioBackend().pause()
            self.dockmanager.pause()

        if recording and not self.display_timer.isActive():
            self.logger.info("Timer start")
            self.display_timer.start()
            self._main_window_view_model.toolbar_view_model.recording = True
            self.playback_widget.start_recording()
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
    # parse command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--python",
        action="store_true",
        help="Print data to friture.cprof")

    parser.add_argument(
        "--kcachegrind",
        action="store_true")

    parser.add_argument(
        "--no-splash",
        action="store_true",
        help="Disable the splash screen on startup")

    program_arguments, remaining_arguments = parser.parse_known_args()
    remaining_arguments.insert(0, sys.argv[0])

    # make the Python warnings go to Friture logger
    logging.captureWarnings(True)

    logFormat = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    formatter = logging.Formatter(logFormat)

    logFileName = "friture.log.txt"
    logDir = platformdirs.user_log_dir("Friture", "")
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
        if "QT_AUTO_SCREEN_SCALE_FACTOR" not in os.environ:
            os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        # set the App ID for Windows 7 to properly display the icon in the
        # taskbar.
        import ctypes
        myappid = 'Friture.Friture.Friture.current'  # arbitrary string
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            logger.error("Could not set the app model ID. If the plaftorm is older than Windows 7, this is normal.")

    app = QApplication(remaining_arguments)

    if platform.system() == "Darwin":
        logger.info("Applying Mac OS-specific setup")
        # help the packaged application find the Qt plugins (imageformats and platforms)
        pluginsPath = os.path.normpath(os.path.join(QApplication.applicationDirPath(), os.path.pardir, 'PlugIns'))
        logger.info("Adding the following to the Library paths: %s", pluginsPath)
        QApplication.addLibraryPath(pluginsPath)

    if platform.system() == "Linux":
        if "PIPEWIRE_ALSA" not in os.environ:
            os.environ['PIPEWIRE_ALSA'] = '{ application.name = "Friture" }'

    # Set the style for Qt Quick Controls
    # We choose the Fusion style as it is a desktop-oriented style
    # It uses the standard system palettes to provide colors that match the desktop environment.
    if "QT_QUICK_CONTROLS_STYLE" not in os.environ:
        os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

    # Splash screen
    if not program_arguments.no_splash:
        pixmap = QPixmap(":/images/splash.png")
        splash = QSplashScreen(pixmap)
        splash.show()
        splash.showMessage("Initializing the audio subsystem")
        app.processEvents()

    window = Friture()
    window.show()
    if not program_arguments.no_splash:
        splash.hide()

    profile = "no"  # "python" or "kcachegrind" or anything else to disable

    if program_arguments.python:
        profile = "python"
    elif program_arguments.kcachegrind:
        profile = "kcachegrind"

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
