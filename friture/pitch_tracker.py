#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

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

import logging
from PyQt5 import QtWidgets
from PyQt5.QtQuickWidgets import QQuickWidget
import numpy as np

from friture.curve import Curve
from friture.pitch_tracker_settings import (
    DEFAULT_MIN_FREQ,
    DEFAULT_MAX_FREQ,
    DEFAULT_DURATION
)
import friture.plotting.frequency_scales as fscales
from friture.scope_data import Scope_Data
from friture.store import GetStore
from friture.qml_tools import qml_url, raise_if_error

class PitchTrackerWidget(QtWidgets.QWidget):
    def __init__(self, parent, engine):
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)

        self.setObjectName("PitchTracker_Widget")

        store = GetStore()
        self._pitch_tracker_data = Scope_Data(store)
        store._dock_states.append(self._pitch_tracker_data)
        state_id = len(store._dock_states) - 1

        self._curve = Curve()
        self._curve.name = "Ch1"
        self._pitch_tracker_data.add_plot_item(self._curve)

        self._pitch_tracker_data.vertical_axis.name = "Frequency (Hz)"
        self._pitch_tracker_data.vertical_axis.setTrackerFormatter(
            lambda x: "%.0f Hz" % (x))
        self._pitch_tracker_data.horizontal_axis.name = "Time (sec)"
        self._pitch_tracker_data.horizontal_axis.setTrackerFormatter(
            lambda x: "%#.3g sec" % (x))

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(2, 2, 2, 2)

        self.quickWidget = QQuickWidget(engine, self)
        self.quickWidget.statusChanged.connect(self.on_status_changed)
        self.quickWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.quickWidget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.quickWidget.setSource(qml_url("Scope.qml"))

        raise_if_error(self.quickWidget)

        self.quickWidget.rootObject().setProperty("stateId", state_id)

        self.gridLayout.addWidget(self.quickWidget, 0, 0, 1, 1)

        self.min_freq = DEFAULT_MIN_FREQ
        self.max_freq = DEFAULT_MAX_FREQ
        self._pitch_tracker_data.vertical_axis.setRange(
            self.min_freq, self.max_freq)
        self._pitch_tracker_data.vertical_axis.setScale(fscales.Octave)

        self.duration = DEFAULT_DURATION
        self._pitch_tracker_data.horizontal_axis.setRange(-self.duration, 0.)

        self.audiobuffer = None

        self._curve.setData(np.array([0.0, 0.75]), np.array([0.0, 0.5]))

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata):
        pass

    def on_status_changed(self, status):
        if status == QQuickWidget.Error:
            for error in self.quickWidget.errors():
                self.logger.error("QML error: " + error.toString())

    # method
    def canvasUpdate(self):
        # nothing to do here
        return

    def setmin(self, value):
        self.min_freq = value
        self._pitch_tracker_data.vertical_axis.setRange(self.min_freq, self.max_freq)

    def setmax(self, value):
        self.max_freq = value
        self._pitch_tracker_data.vertical_axis.setRange(self.min_freq, self.max_freq)

    def setduration(self, value):
        self.duration = value
        self._pitch_tracker_data.horizontal_axis.setRange(-self.duration, 0.)

    # slot
    def settings_called(self, checked):
        # self.settings_dialog.show()
        pass

    # method
    def saveState(self, settings):
        # self.settings_dialog.saveState(settings)
        pass

    # method
    def restoreState(self, settings):
        # self.settings_dialog.restoreState(settings)
        pass
