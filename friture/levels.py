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

from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from friture.levels_settings import Levels_Settings_Dialog  # settings dialog
from friture.qsynthmeter import qsynthMeter
from friture.audioproc import audioproc

from friture_extensions.exp_smoothing_conv import pyx_exp_smoothed_value

from friture.audiobackend import SAMPLING_RATE

STYLESHEET = """
qsynthMeter {
#border: 1px solid gray;
#border-radius: 2px;
padding: 1px;
}
"""

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
LEVEL_TEXT_LABEL_PERIOD_MS = 250

LEVEL_TEXT_LABEL_STEPS = LEVEL_TEXT_LABEL_PERIOD_MS / SMOOTH_DISPLAY_TIMER_PERIOD_MS


class Levels_Widget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Levels_Widget")

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)

        self.label_peak = QtWidgets.QLabel(self)
        self.label_peak.setFont(font)
        # QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft
        self.label_peak.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)
        self.label_peak.setObjectName("label_peak")

        self.label_peak_legend = QtWidgets.QLabel(self)
        self.label_peak_legend.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        self.label_peak_legend.setObjectName("label_peak_legend")

        self.label_rms = QtWidgets.QLabel(self)
        self.label_rms.setFont(font)
        self.label_rms.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)
        self.label_rms.setObjectName("label_rms")

        self.label_rms_legend = QtWidgets.QLabel(self)
        self.label_rms_legend.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        self.label_rms_legend.setObjectName("label_rms_legend")

        self.meter = qsynthMeter(self)
        self.meter.setStyleSheet(STYLESHEET)
        self.meter.setObjectName("meter")

        self.gridLayout.addWidget(self.label_peak, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.label_peak_legend, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.label_rms, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.label_rms_legend, 3, 0, 1, 1)

        self.gridLayout.addWidget(self.meter, 4, 0, 1, 1)

        self.label_rms.setText("+00.0")
        self.label_peak.setText("+00.0")
        self.label_rms_legend.setText("dB FS\n RMS")
        self.label_peak_legend.setText("dB FS\n Peak")
        self.label_rms.setTextFormat(QtCore.Qt.PlainText)
        self.label_peak.setTextFormat(QtCore.Qt.PlainText)
        # self.label_rms.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        # self.label_rms_legend.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        # self.label_peak.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        # self.label_peak_legend.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

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
        self.level_rms = -30.
        self.level_max = -30.
        self.old_rms = 1e-30
        self.old_max = 1e-30
        # second channel
        self.level_rms_2 = -30.
        self.level_max_2 = -30.
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
            self.meter.setPortCount(2)
            self.two_channels = True
        elif floatdata.shape[0] == 1 and self.two_channels:
            self.meter.setPortCount(1)
            self.two_channels = False

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

        self.level_rms = 10. * np.log10(value_rms + 0. * 1e-80)
        self.level_max = 20. * np.log10(self.old_max + 0. * 1e-80)

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

            self.level_rms_2 = 10. * np.log10(value_rms + 0. * 1e-80)
            self.level_max_2 = 20. * np.log10(self.old_max_2 + 0. * 1e-80)

    # method
    def canvasUpdate(self):
        if not self.isVisible():
            return

        self.i += 1

        if self.i == LEVEL_TEXT_LABEL_STEPS:
            if self.level_rms > -150.:
                string_rms = "%+05.01f" % self.level_rms
            else:
                string_rms = "-Inf"
            if self.level_max > -150.:
                string_peak = "%+05.01f" % self.level_max
            else:
                string_peak = "-Inf"

            self.label_rms.setText(string_rms)
            self.label_peak.setText(string_peak)

        self.meter.setValue(0, self.level_rms, self.level_max)

        if self.two_channels:
            self.meter.setValue(0, self.level_rms, self.level_max)
            self.meter.setValue(1, self.level_rms_2, self.level_max_2)

            if self.i == LEVEL_TEXT_LABEL_STEPS:
                if self.level_rms_2 > -150.:
                    string_rms_2 = "%+05.01f" % self.level_rms_2
                else:
                    string_rms_2 = "-Inf"
                if self.level_max_2 > -150.:
                    string_peak_2 = "%+05.01f" % self.level_max_2
                else:
                    string_peak_2 = "-Inf"

                self.label_rms.setText("1: %s\n2: %s" % (string_rms, string_rms_2))
                self.label_peak.setText("1: %s\n2: %s" % (string_peak, string_peak_2))

        self.i = self.i % LEVEL_TEXT_LABEL_STEPS

        # prevent re-layout
        self.label_rms.setMinimumWidth(self.label_rms.width())

    # slot
    def settings_called(self, checked):
        self.settings_dialog.show()

    # method
    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    # method
    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)
