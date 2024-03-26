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

from PyQt5 import QtWidgets

from friture.audiobackend import SAMPLING_RATE

# Roughly the maximum singing range:
DEFAULT_MIN_FREQ = 80
DEFAULT_MAX_FREQ = 1000
DEFAULT_DURATION = 30
DEFAULT_MIN_SNR = 3.0
DEFAULT_FFT_SIZE = 16384

class PitchTrackerSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Pitch Tracker Settings")
        self.form_layout = QtWidgets.QFormLayout(self)

        self.min_freq = QtWidgets.QSpinBox(self)
        self.min_freq.setMinimum(10)
        self.min_freq.setMaximum(SAMPLING_RATE // 2)
        self.min_freq.setSingleStep(10)
        self.min_freq.setValue(DEFAULT_MIN_FREQ)
        self.min_freq.setSuffix(" Hz")
        self.min_freq.setObjectName("min_freq")
        self.min_freq.valueChanged.connect(self.parent().set_min_freq)
        self.form_layout.addRow("Min:", self.min_freq)

        self.max_freq = QtWidgets.QSpinBox(self)
        self.max_freq.setMinimum(10)
        self.max_freq.setMaximum(SAMPLING_RATE // 2)
        self.max_freq.setSingleStep(10)
        self.max_freq.setValue(DEFAULT_MAX_FREQ)
        self.max_freq.setSuffix(" Hz")
        self.max_freq.setObjectName("max_freq")
        self.max_freq.valueChanged.connect(self.parent().set_max_freq)
        self.form_layout.addRow("Max:", self.max_freq)

        self.duration = QtWidgets.QSpinBox(self)
        self.duration.setMinimum(5)
        self.duration.setMaximum(600)
        self.duration.setSingleStep(1)
        self.duration.setValue(DEFAULT_DURATION)
        self.duration.setSuffix(" s")
        self.duration.setObjectName("duration")
        self.duration.valueChanged.connect(self.parent().set_duration)
        self.form_layout.addRow("Duration:", self.duration)

        self.min_snr = QtWidgets.QDoubleSpinBox(self)
        self.min_snr.setMinimum(0)
        self.min_snr.setMaximum(50)
        self.min_snr.setSingleStep(1)
        self.min_snr.setValue(DEFAULT_MIN_SNR)
        self.min_snr.setSuffix(" dB")
        self.min_snr.setObjectName("min_snr")
        self.min_snr.valueChanged.connect(self.parent().set_min_snr)
        self.form_layout.addRow("Min SNR:", self.min_snr)

        self.setLayout(self.form_layout)

    def save_state(self, settings):
        settings.setValue("min_freq", self.min_freq.value())
        settings.setValue("max_freq", self.max_freq.value())
        settings.setValue("duration", self.duration.value())
        settings.setValue("min_snr", self.min_snr.value())

    def restore_state(self, settings):
        self.min_freq.setValue(
            settings.value("min_freq", DEFAULT_MIN_FREQ, type=int))
        self.max_freq.setValue(
            settings.value("max_freq", DEFAULT_MAX_FREQ, type=int))
        self.duration.setValue(
            settings.value("duration", DEFAULT_DURATION, type=int))
        self.min_snr.setValue(
            settings.value("min_snr", DEFAULT_MIN_SNR, type=float))
