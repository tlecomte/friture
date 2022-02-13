#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

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

"""Level widget that displays peak and RMS levels for 1 or 2 ports."""

from PyQt5 import QtWidgets
from PyQt5.QtQml import QQmlComponent
from PyQt5.QtQuick import QQuickWindow
import numpy as np

from friture.store import GetStore
from friture.levels_settings import Levels_Settings_Dialog  # settings dialog
from friture.audioproc import audioproc
from friture.level_view_model import LevelViewModel
from friture.iec import dB_to_IEC
from friture_extensions.exp_smoothing_conv import pyx_exp_smoothed_value
from friture.audiobackend import SAMPLING_RATE
from friture.qml_tools import qml_url, raise_if_error

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
LEVEL_TEXT_LABEL_PERIOD_MS = 250

LEVEL_TEXT_LABEL_STEPS = LEVEL_TEXT_LABEL_PERIOD_MS / SMOOTH_DISPLAY_TIMER_PERIOD_MS

class Levels_Widget(QtWidgets.QWidget):

    def __init__(self, parent, engine):
        super().__init__(parent)
        self.setObjectName("Levels_Widget")

        self.gridLayout = QtWidgets.QVBoxLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        store = GetStore()
        self.level_view_model = LevelViewModel(store)
        store._dock_states.append(self.level_view_model)
        state_id = len(store._dock_states) - 1

        self.quickWindow = QQuickWindow()
        component = QQmlComponent(engine, qml_url("Levels.qml"), self)
        raise_if_error(component)

        engineContext = engine.rootContext()
        initialProperties = {"parent": self.quickWindow.contentItem(), "stateId": state_id }
        self.qmlObject = component.createWithInitialProperties(initialProperties, engineContext)
        self.qmlObject.setParent(self.quickWindow)

        self.quickWidget = QtWidgets.QWidget.createWindowContainer(self.quickWindow, self)
        self.quickWidget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)       
        self.gridLayout.addWidget(self.quickWidget)

        self.qmlObject.widthChanged.connect(self.onWidthChanged)
        self.onWidthChanged()

        self.audiobuffer = None

        # initialize the settings dialog
        self.settings_dialog = Levels_Settings_Dialog(self)

        # initialize the class instance that will do the fft
        self.proc = audioproc()

        # time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000. #DISPLAY
        # time = 0.025 #IMPULSE setting for a sound level meter
        # time = 0.125 #FAST setting for a sound level meter
        # time = 1. #SLOW setting for a sound level meter
        self.response_time = 0.300  # 300ms is a common value for VU meters
        # an exponential smoothing filter is a simple IIR filter
        # s_i = alpha*x_i + (1-alpha)*s_{i-1}
        # we compute alpha so that the n most recent samples represent 100*w percent of the output
        w = 0.65
        n = self.response_time * SAMPLING_RATE
        N = 5*n
        self.alpha = 1. - (1. - w) ** (1. / (n + 1))
        self.kernel = (1. - self.alpha) ** (np.arange(0, N)[::-1])
        # first channel
        self.old_rms = 1e-30
        self.old_max = 1e-30
        # second channel
        self.old_rms_2 = 1e-30
        self.old_max_2 = 1e-30

        response_time_peaks = 0.025  # 25ms for instantaneous peaks
        n2 = response_time_peaks / (SMOOTH_DISPLAY_TIMER_PERIOD_MS / 1000.)
        self.alpha2 = 1. - (1. - w) ** (1. / (n2 + 1))

        self.two_channels = False

        self.i = 0

    def onWidthChanged(self):
        self.quickWidget.setFixedWidth(int(self.qmlObject.width()))

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata):
        if floatdata.shape[0] > 1 and not self.two_channels:
            self.two_channels = True
            self.level_view_model.two_channels = True
        elif floatdata.shape[0] == 1 and self.two_channels:
            self.two_channels = False
            self.level_view_model.two_channels = False

        # first channel
        y1 = floatdata[0, :]

        # exponential smoothing for max
        if len(y1) > 0:
            value_max = np.abs(y1).max()
            if value_max > self.old_max * (1. - self.alpha2):
                self.old_max = value_max
            else:
                # exponential decrease
                self.old_max *= (1. - self.alpha2)

        # exponential smoothing for RMS
        value_rms = pyx_exp_smoothed_value(self.kernel, self.alpha, y1 ** 2, self.old_rms)
        self.old_rms = value_rms

        self.level_view_model.level_data.level_rms = 10. * np.log10(value_rms + 0. * 1e-80)
        self.level_view_model.level_data.level_max = 20. * np.log10(self.old_max + 0. * 1e-80)
        self.level_view_model.level_data_ballistic.peak_iec = dB_to_IEC(max(self.level_view_model.level_data.level_max, self.level_view_model.level_data.level_rms))

        if self.two_channels:
            # second channel
            y2 = floatdata[1, :]

            # exponential smoothing for max
            if len(y2) > 0:
                value_max = np.abs(y2).max()
                if value_max > self.old_max_2 * (1. - self.alpha2):
                    self.old_max_2 = value_max
                else:
                    # exponential decrease
                    self.old_max_2 *= (1. - self.alpha2)

            # exponential smoothing for RMS
            value_rms = pyx_exp_smoothed_value(self.kernel, self.alpha, y2 ** 2, self.old_rms_2)
            self.old_rms_2 = value_rms

            self.level_view_model.level_data_2.level_rms = 10. * np.log10(value_rms + 0. * 1e-80)
            self.level_view_model.level_data_2.level_max = 20. * np.log10(self.old_max_2 + 0. * 1e-80)
            self.level_view_model.level_data_ballistic_2.peak_iec = dB_to_IEC(max(self.level_view_model.level_data_2.level_max, self.level_view_model.level_data_2.level_rms))

    # method
    def canvasUpdate(self):
        if not self.isVisible():
            return

        self.i += 1

        if self.i == LEVEL_TEXT_LABEL_STEPS:
            self.level_view_model.level_data_slow.level_rms = self.level_view_model.level_data.level_rms
            self.level_view_model.level_data_slow.level_max = self.level_view_model.level_data.level_max

            if self.two_channels:
                self.level_view_model.level_data_slow_2.level_rms = self.level_view_model.level_data_2.level_rms
                self.level_view_model.level_data_slow_2.level_max = self.level_view_model.level_data_2.level_max
 
        self.i = self.i % LEVEL_TEXT_LABEL_STEPS

    # slot
    def settings_called(self, checked):
        self.settings_dialog.show()

    # method
    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    # method
    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)
