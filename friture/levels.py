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

import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtQuickWidgets import QQuickWidget

from PyQt5.QtCore import pyqtProperty
import numpy as np
from friture.levels_settings import Levels_Settings_Dialog  # settings dialog
from friture.audioproc import audioproc

from friture_extensions.exp_smoothing_conv import pyx_exp_smoothed_value

from friture.audiobackend import SAMPLING_RATE

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
LEVEL_TEXT_LABEL_PERIOD_MS = 250

LEVEL_TEXT_LABEL_STEPS = LEVEL_TEXT_LABEL_PERIOD_MS / SMOOTH_DISPLAY_TIMER_PERIOD_MS

PEAK_DECAY_RATE = (1.0 - 3E-6/500.)
# Number of cycles the peak stays on hold before fall-off.
PEAK_FALLOFF = 32

def dB_to_IEC(dB):
    if dB < -70.0:
        return 0.0
    elif dB < -60.0:
        return (dB + 70.0) * 0.0025
    elif dB < -50.0:
        return (dB + 60.0) * 0.005 + 0.025
    elif dB < -40.0:
        return (dB + 50.0) * 0.0075 + 0.075
    elif dB < -30.0:
        return (dB + 40.0) * 0.015 + 0.15
    elif dB < -20.0:
        return (dB + 30.0) * 0.02 + 0.3
    else:  # if dB < 0.0
        return (dB + 20.0) * 0.025 + 0.5

class LevelData(QtCore.QObject):
    level_rms_changed = QtCore.pyqtSignal(float)
    level_max_changed = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._level_rms = -30.
        self._level_max = -30.

    @pyqtProperty(float, notify=level_rms_changed)
    def level_rms(self):
        return self._level_rms
    
    @pyqtProperty(float, notify=level_rms_changed)
    def level_rms_iec(self):
        return dB_to_IEC(self._level_rms)
    
    @level_rms.setter
    def level_rms(self, level_rms):
        if self._level_rms != level_rms:
            self._level_rms = level_rms
            self.level_rms_changed.emit(level_rms)

    @pyqtProperty(float, notify=level_max_changed)
    def level_max(self):
        return self._level_max

    @pyqtProperty(float, notify=level_max_changed)
    def level_max_iec(self):
        return dB_to_IEC(self._level_max)
    
    @level_max.setter
    def level_max(self, level_max):
        if self._level_max != level_max:
            self._level_max = level_max
            self.level_max_changed.emit(level_max)

class BallisticPeak(QtCore.QObject):
    peak_changed = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._peak_iec = 0
        self._peak_hold_counter = 0
        self._peak_decay_factor = PEAK_DECAY_RATE

    @pyqtProperty(float, notify=peak_changed)
    def peak_iec(self):
        return self._peak_iec
    
    @peak_iec.setter
    def peak_iec(self, peak_iec):

        # peak-hold-then-decay mechanism
        if peak_iec > self._peak_iec:
            # follow the peak
            new_peak_iec = peak_iec
            self._peak_hold_counter = 0  # reset the hold
            self._peak_decay_factor = PEAK_DECAY_RATE
        elif self._peak_hold_counter + 1 <= PEAK_FALLOFF:
            # hold
            new_peak_iec = self._peak_iec
            self._peak_hold_counter += 1
        else:
            # decay
            new_peak_iec = self._peak_decay_factor * float(self._peak_iec)
            if new_peak_iec < peak_iec:
                new_peak_iec = peak_iec
                self._peak_hold_counter = 0  # reset the hold
                self._peak_decay_factor = PEAK_DECAY_RATE
            else:
                self._peak_decay_factor *= self._peak_decay_factor

        if self._peak_iec != new_peak_iec:
            self._peak_iec = new_peak_iec
            self.peak_changed.emit(new_peak_iec)

class LevelSettings(QtCore.QObject):
    two_channels_changed = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._two_channels = False

    @pyqtProperty(bool, notify=two_channels_changed)
    def two_channels(self):
        return self._two_channels
    
    @two_channels.setter
    def two_channels(self, two_channels):
        if self._two_channels != two_channels:
            self._two_channels = two_channels
            self.two_channels_changed.emit(two_channels)

class Levels_Widget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Levels_Widget")

        self.gridLayout = QtWidgets.QVBoxLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        self.level_data = LevelData(self)
        self.level_data_2 = LevelData(self)
        self.level_data_slow = LevelData(self)
        self.level_data_slow_2 = LevelData(self)
        self.level_data_ballistic = BallisticPeak(self)
        self.level_data_ballistic_2 = BallisticPeak(self)
        self.level_settings = LevelSettings(self)

        CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(CURRENT_DIR, "LevelsText.qml")
        self.quickWidgetText = QQuickWidget(self)
        self.quickWidgetText.setResizeMode(QQuickWidget.SizeViewToRootObject)
        rootContext = self.quickWidgetText.engine().rootContext()
        rootContext.setContextProperty("level_settings", self.level_settings)
        rootContext.setContextProperty("level_data_slow", self.level_data_slow)
        rootContext.setContextProperty("level_data_slow_2", self.level_data_slow_2)
        self.quickWidgetText.setSource(QtCore.QUrl.fromLocalFile(filename))
        self.gridLayout.addWidget(self.quickWidgetText)

        filename = os.path.join(CURRENT_DIR, "LevelsMeter.qml")
        self.quickWidget = QQuickWidget(self)
        self.quickWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        rootContext = self.quickWidget.engine().rootContext()
        rootContext.setContextProperty("level_settings", self.level_settings)
        rootContext.setContextProperty("level_data", self.level_data)
        rootContext.setContextProperty("level_data_2", self.level_data_2)
        rootContext.setContextProperty("level_data_ballistic", self.level_data_ballistic)
        rootContext.setContextProperty("level_data_ballistic_2", self.level_data_ballistic_2)
        self.quickWidget.setSource(QtCore.QUrl.fromLocalFile(filename))
        self.quickWidget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addWidget(self.quickWidget)

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

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata):
        if floatdata.shape[0] > 1 and not self.two_channels:
            self.two_channels = True
            self.level_settings.two_channels = True
        elif floatdata.shape[0] == 1 and self.two_channels:
            self.two_channels = False
            self.level_settings.two_channels = False

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

        self.level_data.level_rms = 10. * np.log10(value_rms + 0. * 1e-80)
        self.level_data.level_max = 20. * np.log10(self.old_max + 0. * 1e-80)
        self.level_data_ballistic.peak_iec = dB_to_IEC(max(self.level_data.level_max, self.level_data.level_rms))

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

            self.level_data_2.level_rms = 10. * np.log10(value_rms + 0. * 1e-80)
            self.level_data_2.level_max = 20. * np.log10(self.old_max_2 + 0. * 1e-80)
            self.level_data_ballistic_2.peak_iec = dB_to_IEC(max(self.level_data_2.level_max, self.level_data_2.level_rms))

    # method
    def canvasUpdate(self):
        if not self.isVisible():
            return

        self.i += 1

        if self.i == LEVEL_TEXT_LABEL_STEPS:
            self.level_data_slow.level_rms = self.level_data.level_rms
            self.level_data_slow.level_max = self.level_data.level_max

            if self.two_channels:
                self.level_data_slow_2.level_rms = self.level_data_2.level_rms
                self.level_data_slow_2.level_max = self.level_data_2.level_max
 
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
