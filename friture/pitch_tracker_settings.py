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
from PyQt5.QtCore import QSettings
from typing import Any

from friture.audiobackend import SAMPLING_RATE

# Pitch tracker defaults:
DEFAULT_FFT_SIZE = 4096
DEFAULT_MIN_FREQ = 65
DEFAULT_MAX_FREQ = 1047
DEFAULT_DURATION = 10
DEFAULT_MIN_DB = -50.0
DEFAULT_C_RES = 10      # Pitch resolution in cents. Default of 10 produces 120 kernels per octave.
DEFAULT_P_CONF = 0.50   # Confidence threshold for pitch estimation. Unitless.
DEFAULT_P_DELTA = 2     # Maximum pitch jump between frames in semitones.

class PitchTrackerSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget, view_model: Any) -> None:
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
        self.min_freq.valueChanged.connect(view_model.set_min_freq) # type: ignore
        self.form_layout.addRow("Min:", self.min_freq)

        self.max_freq = QtWidgets.QSpinBox(self)
        self.max_freq.setMinimum(10)
        self.max_freq.setMaximum(SAMPLING_RATE // 2)
        self.max_freq.setSingleStep(10)
        self.max_freq.setValue(DEFAULT_MAX_FREQ)
        self.max_freq.setSuffix(" Hz")
        self.max_freq.setObjectName("max_freq")
        self.max_freq.valueChanged.connect(view_model.set_max_freq) # type: ignore
        self.form_layout.addRow("Max:", self.max_freq)

        self.duration = QtWidgets.QSpinBox(self)
        self.duration.setMinimum(5)
        self.duration.setMaximum(60)
        self.duration.setSingleStep(1)
        self.duration.setValue(DEFAULT_DURATION)
        self.duration.setSuffix(" s")
        self.duration.setObjectName("duration")
        self.duration.valueChanged.connect(view_model.set_duration) # type: ignore
        self.form_layout.addRow("Duration:", self.duration)

        self.conf = QtWidgets.QDoubleSpinBox(self)
        self.conf.setMinimum(0)
        self.conf.setMaximum(1)
        self.conf.setSingleStep(0.01)
        self.conf.setValue(DEFAULT_P_CONF)
        self.conf.setSuffix("")
        self.conf.setObjectName("conf")
        self.conf.valueChanged.connect(view_model.set_conf)
        self.form_layout.addRow("Conf. Cut:", self.conf)

        self.min_db = QtWidgets.QDoubleSpinBox(self)
        self.min_db.setMinimum(-100)
        self.min_db.setMaximum(0)
        self.min_db.setSingleStep(1)
        self.min_db.setValue(DEFAULT_MIN_DB)
        self.min_db.setSuffix(" dB")
        self.min_db.setObjectName("min_db")
        self.min_db.valueChanged.connect(view_model.set_min_db) # type: ignore
        self.form_layout.addRow("Min Amplitude:", self.min_db)

        self.setLayout(self.form_layout)

    def save_state(self, settings: QSettings) -> None:
        settings.setValue("min_freq", self.min_freq.value())
        settings.setValue("max_freq", self.max_freq.value())
        settings.setValue("duration", self.duration.value())
        settings.setValue("conf", self.conf.value())
        settings.setValue("min_db", self.min_db.value())

    def restore_state(self, settings: QSettings) -> None:
        self.min_freq.setValue(
            settings.value("min_freq", DEFAULT_MIN_FREQ, type=int))
        self.max_freq.setValue(
            settings.value("max_freq", DEFAULT_MAX_FREQ, type=int))
        self.duration.setValue(
            settings.value("duration", DEFAULT_DURATION, type=int))
        self.conf.setValue(
            settings.value("conf", DEFAULT_P_CONF, type=float))
        self.min_db.setValue(
            settings.value("min_db", DEFAULT_MIN_DB, type=float))

