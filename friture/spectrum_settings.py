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

import logging

from PyQt5 import QtWidgets
from friture.audiobackend import SAMPLING_RATE

# shared with spectrum_settings.py
DEFAULT_FFT_SIZE = 8  # 8192 points
DEFAULT_FREQ_SCALE = 1  # log10
DEFAULT_MAXFREQ = 20000
DEFAULT_MINFREQ = 20
DEFAULT_SPEC_MIN = -100
DEFAULT_SPEC_MAX = -20
DEFAULT_WEIGHTING = 1  # A
DEFAULT_SHOW_FREQ_LABELS = True
DEFAULT_RESPONSE_TIME = 0.025
DEFAULT_RESPONSE_TIME_INDEX = 0


class Spectrum_Settings_Dialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)

        self.setWindowTitle("Spectrum settings")

        self.formLayout = QtWidgets.QFormLayout(self)

        self.comboBox_dual_channel = QtWidgets.QComboBox(self)
        self.comboBox_dual_channel.setObjectName("dual")
        self.comboBox_dual_channel.addItem("Single-channel")
        self.comboBox_dual_channel.addItem("Dual-channel")
        self.comboBox_dual_channel.setCurrentIndex(0)

        self.comboBox_fftsize = QtWidgets.QComboBox(self)
        self.comboBox_fftsize.setObjectName("comboBox_fftsize")
        self.comboBox_fftsize.addItem("32 points")
        self.comboBox_fftsize.addItem("64 points")
        self.comboBox_fftsize.addItem("128 points")
        self.comboBox_fftsize.addItem("256 points")
        self.comboBox_fftsize.addItem("512 points")
        self.comboBox_fftsize.addItem("1024 points")
        self.comboBox_fftsize.addItem("2048 points")
        self.comboBox_fftsize.addItem("4096 points")
        self.comboBox_fftsize.addItem("8192 points")
        self.comboBox_fftsize.addItem("16384 points")
        self.comboBox_fftsize.setCurrentIndex(DEFAULT_FFT_SIZE)

        self.comboBox_freqscale = QtWidgets.QComboBox(self)
        self.comboBox_freqscale.setObjectName("comboBox_freqscale")
        self.comboBox_freqscale.addItem("Linear")
        self.comboBox_freqscale.addItem("Logarithmic")
        self.comboBox_freqscale.setCurrentIndex(DEFAULT_FREQ_SCALE)

        self.spinBox_minfreq = QtWidgets.QSpinBox(self)
        self.spinBox_minfreq.setMinimum(20)
        self.spinBox_minfreq.setMaximum(SAMPLING_RATE / 2)
        self.spinBox_minfreq.setSingleStep(10)
        self.spinBox_minfreq.setValue(DEFAULT_MINFREQ)
        self.spinBox_minfreq.setObjectName("spinBox_minfreq")
        self.spinBox_minfreq.setSuffix(" Hz")

        self.spinBox_maxfreq = QtWidgets.QSpinBox(self)
        self.spinBox_maxfreq.setMinimum(20)
        self.spinBox_maxfreq.setMaximum(SAMPLING_RATE / 2)
        self.spinBox_maxfreq.setSingleStep(1000)
        self.spinBox_maxfreq.setProperty("value", DEFAULT_MAXFREQ)
        self.spinBox_maxfreq.setObjectName("spinBox_maxfreq")
        self.spinBox_maxfreq.setSuffix(" Hz")

        self.spinBox_specmin = QtWidgets.QSpinBox(self)
        self.spinBox_specmin.setKeyboardTracking(False)
        self.spinBox_specmin.setMinimum(-200)
        self.spinBox_specmin.setMaximum(200)
        self.spinBox_specmin.setProperty("value", DEFAULT_SPEC_MIN)
        self.spinBox_specmin.setObjectName("spinBox_specmin")
        self.spinBox_specmin.setSuffix(" dB")

        self.spinBox_specmax = QtWidgets.QSpinBox(self)
        self.spinBox_specmax.setKeyboardTracking(False)
        self.spinBox_specmax.setMinimum(-200)
        self.spinBox_specmax.setMaximum(200)
        self.spinBox_specmax.setProperty("value", DEFAULT_SPEC_MAX)
        self.spinBox_specmax.setObjectName("spinBox_specmax")
        self.spinBox_specmax.setSuffix(" dB")

        self.comboBox_weighting = QtWidgets.QComboBox(self)
        self.comboBox_weighting.setObjectName("weighting")
        self.comboBox_weighting.addItem("None")
        self.comboBox_weighting.addItem("A")
        self.comboBox_weighting.addItem("B")
        self.comboBox_weighting.addItem("C")
        self.comboBox_weighting.setCurrentIndex(DEFAULT_WEIGHTING)

        self.comboBox_response_time = QtWidgets.QComboBox(self)
        self.comboBox_response_time.setObjectName("response_time")
        self.comboBox_response_time.addItem("25 ms (Impulse)")
        self.comboBox_response_time.addItem("125 ms (Fast)")
        self.comboBox_response_time.addItem("300 ms")
        self.comboBox_response_time.addItem("1s (Slow)")
        self.comboBox_response_time.setCurrentIndex(DEFAULT_RESPONSE_TIME_INDEX)

        self.checkBox_showFreqLabels = QtWidgets.QCheckBox(self)
        self.checkBox_showFreqLabels.setObjectName("showFreqLabels")
        self.checkBox_showFreqLabels.setChecked(DEFAULT_SHOW_FREQ_LABELS)

        self.formLayout.addRow("Measurement type:", self.comboBox_dual_channel)
        self.formLayout.addRow("FFT Size:", self.comboBox_fftsize)
        self.formLayout.addRow("Frequency scale:", self.comboBox_freqscale)
        self.formLayout.addRow("Min frequency:", self.spinBox_minfreq)
        self.formLayout.addRow("Max frequency:", self.spinBox_maxfreq)
        self.formLayout.addRow("Min:", self.spinBox_specmin)
        self.formLayout.addRow("Max:", self.spinBox_specmax)
        self.formLayout.addRow("Middle-ear weighting:", self.comboBox_weighting)
        self.formLayout.addRow("Response time:", self.comboBox_response_time)
        self.formLayout.addRow("Display max-frequency label:", self.checkBox_showFreqLabels)

        self.setLayout(self.formLayout)

        self.comboBox_dual_channel.currentIndexChanged.connect(self.dualchannelchanged)
        self.comboBox_fftsize.currentIndexChanged.connect(self.fftsizechanged)
        self.comboBox_freqscale.currentIndexChanged.connect(self.freqscalechanged)
        self.spinBox_minfreq.valueChanged.connect(self.parent().setminfreq)
        self.spinBox_maxfreq.valueChanged.connect(self.parent().setmaxfreq)
        self.spinBox_specmin.valueChanged.connect(self.parent().setmin)
        self.spinBox_specmax.valueChanged.connect(self.parent().setmax)
        self.comboBox_weighting.currentIndexChanged.connect(self.parent().setweighting)
        self.comboBox_response_time.currentIndexChanged.connect(self.responsetimechanged)
        self.checkBox_showFreqLabels.toggled.connect(self.parent().setShowFreqLabel)

    # slot
    def dualchannelchanged(self, index):
        if index == 0:
            self.parent().setdualchannels(False)
        else:
            self.parent().setdualchannels(True)

    # slot
    def fftsizechanged(self, index):
        self.logger.info("fft_size_changed slot %d %d %f", index, 2 ** index * 32, 150000 / 2 ** index * 32)
        # FIXME the size should not be found from the index, but attached as item data
        fft_size = 2 ** index * 32
        self.parent().setfftsize(fft_size)

    # slot
    def freqscalechanged(self, index):
        self.logger.info("freq_scale slot %d", index)
        if index == 1:
            self.parent().PlotZoneSpect.setlogfreqscale()
        else:
            self.parent().PlotZoneSpect.setlinfreqscale()

    # slot
    def responsetimechanged(self, index):
        if index == 0:
            response_time = 0.025
        elif index == 1:
            response_time = 0.125
        elif index == 2:
            response_time = 0.3
        elif index == 3:
            response_time = 1.
        self.logger.info("responsetimechanged slot %d %d", index, response_time)
        self.parent().setresponsetime(response_time)

    # method
    def saveState(self, settings):
        settings.setValue("fftSize", self.comboBox_fftsize.currentIndex())
        settings.setValue("freqScale", self.comboBox_freqscale.currentIndex())
        settings.setValue("freqMin", self.spinBox_minfreq.value())
        settings.setValue("freqMax", self.spinBox_maxfreq.value())
        settings.setValue("Min", self.spinBox_specmin.value())
        settings.setValue("Max", self.spinBox_specmax.value())
        settings.setValue("weighting", self.comboBox_weighting.currentIndex())
        settings.setValue("responseTime", self.comboBox_response_time.currentIndex())
        settings.setValue("showFreqLabels", self.checkBox_showFreqLabels.isChecked())

    # method
    def restoreState(self, settings):
        fft_size = settings.value("fftSize", DEFAULT_FFT_SIZE, type=int)  # 7th index is 1024 points
        self.comboBox_fftsize.setCurrentIndex(fft_size)
        freqscale = settings.value("freqScale", DEFAULT_FREQ_SCALE, type=int)
        self.comboBox_freqscale.setCurrentIndex(freqscale)
        freqMin = settings.value("freqMin", DEFAULT_MINFREQ, type=int)
        self.spinBox_minfreq.setValue(freqMin)
        freqMax = settings.value("freqMax", DEFAULT_MAXFREQ, type=int)
        self.spinBox_maxfreq.setValue(freqMax)
        colorMin = settings.value("Min", DEFAULT_SPEC_MIN, type=int)
        self.spinBox_specmin.setValue(colorMin)
        colorMax = settings.value("Max", DEFAULT_SPEC_MAX, type=int)
        self.spinBox_specmax.setValue(colorMax)
        weighting = settings.value("weighting", DEFAULT_WEIGHTING, type=int)
        self.comboBox_weighting.setCurrentIndex(weighting)
        responseTime = settings.value("responseTime", DEFAULT_RESPONSE_TIME_INDEX, type=int)
        self.comboBox_response_time.setCurrentIndex(responseTime)
        showFreqLabels = settings.value("showFreqLabels", DEFAULT_SHOW_FREQ_LABELS, type=bool)
        self.checkBox_showFreqLabels.setChecked(showFreqLabels)
