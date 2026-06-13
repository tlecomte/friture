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

from PyQt5 import QtWidgets

from friture.settings_dialog_layout import create_form_layout

DEFAULT_MAXTIME = 600
DEFAULT_LEVEL_MIN = -70
DEFAULT_LEVEL_MAX = -20
DEFAULT_RESPONSE_TIME = 20
DEFAULT_CALIBRATION_OFFSET_DB = 0.0
DEFAULT_UNIT_LABEL = "dB FS"

UNIT_PRESETS = ["dB FS", "dBSPL", "dBu", "dB"]


class LongLevels_Settings_Dialog(QtWidgets.QDialog):

    def __init__(self, parent, view_model):
        super().__init__(parent)

        self._widget = view_model
        self.setWindowTitle("Long levels settings")

        self.formLayout = create_form_layout(self)

        self.spinBox_specmin = QtWidgets.QSpinBox(self)
        self.spinBox_specmin.setKeyboardTracking(False)
        self.spinBox_specmin.setMinimum(-200)
        self.spinBox_specmin.setMaximum(200)
        self.spinBox_specmin.setProperty("value", DEFAULT_LEVEL_MIN)
        self.spinBox_specmin.setObjectName("longlevels_specmin")
        self.spinBox_specmin.setSuffix(" dB")

        self.spinBox_specmax = QtWidgets.QSpinBox(self)
        self.spinBox_specmax.setKeyboardTracking(False)
        self.spinBox_specmax.setMinimum(-200)
        self.spinBox_specmax.setMaximum(200)
        self.spinBox_specmax.setProperty("value", DEFAULT_LEVEL_MAX)
        self.spinBox_specmax.setObjectName("longlevels_specmax")
        self.spinBox_specmax.setSuffix(" dB")

        self.spinBox_resptime = QtWidgets.QSpinBox(self)
        self.spinBox_resptime.setKeyboardTracking(False)
        self.spinBox_resptime.setMinimum(1)
        self.spinBox_resptime.setMaximum(20)
        self.spinBox_resptime.setProperty("value", DEFAULT_RESPONSE_TIME)
        self.spinBox_resptime.setObjectName("longlevels_resptime")
        self.spinBox_resptime.setSuffix(" sec")

        self.spinBox_timemax = QtWidgets.QSpinBox(self)
        self.spinBox_timemax.setKeyboardTracking(False)
        self.spinBox_timemax.setMinimum(5)
        self.spinBox_timemax.setMaximum(3600)
        self.spinBox_timemax.setProperty("value", DEFAULT_MAXTIME)
        self.spinBox_timemax.setObjectName("longlevels_timemax")
        self.spinBox_timemax.setSuffix(" sec")

        self.doubleSpinBox_offset = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_offset.setDecimals(1)
        self.doubleSpinBox_offset.setRange(-200.0, 200.0)
        self.doubleSpinBox_offset.setValue(DEFAULT_CALIBRATION_OFFSET_DB)
        self.doubleSpinBox_offset.setSuffix(" dB")

        self.comboBox_unit = QtWidgets.QComboBox(self)
        for unit in UNIT_PRESETS:
            self.comboBox_unit.addItem(unit)
        self.comboBox_unit.setCurrentText(DEFAULT_UNIT_LABEL)

        self.lineEdit_reference = QtWidgets.QLineEdit(self)
        self.lineEdit_reference.setPlaceholderText("Optional calibration note")

        self.button_calibrate = QtWidgets.QPushButton("Calibrate from current reading…", self)
        self.button_calibrate.clicked.connect(self._calibrate_from_current)

        self.formLayout.addRow("Max:", self.spinBox_specmax)
        self.formLayout.addRow("Min:", self.spinBox_specmin)
        self.formLayout.addRow("Response Time", self.spinBox_resptime)
        self.formLayout.addRow("Time Range:", self.spinBox_timemax)
        self.formLayout.addRow("Calibration offset:", self.doubleSpinBox_offset)
        self.formLayout.addRow("Unit label:", self.comboBox_unit)
        self.formLayout.addRow("Reference note:", self.lineEdit_reference)
        self.formLayout.addRow("", self.button_calibrate)

        self.spinBox_specmin.valueChanged.connect(view_model.setmin)
        self.spinBox_specmax.valueChanged.connect(view_model.setmax)
        self.spinBox_resptime.valueChanged.connect(view_model.setresptime)
        self.spinBox_timemax.valueChanged.connect(view_model.setduration)
        self.doubleSpinBox_offset.valueChanged.connect(view_model.set_calibration_offset)
        self.comboBox_unit.currentTextChanged.connect(view_model.set_unit_label)
        self.lineEdit_reference.textChanged.connect(view_model.set_reference_note)

    def _calibrate_from_current(self) -> None:
        target_db, ok = QtWidgets.QInputDialog.getDouble(
            self,
            "Calibrate level",
            "Current input should read (dB):",
            value=94.0,
            decimals=1,
        )
        if ok:
            self._widget.calibrate_to_target(target_db)
            self.doubleSpinBox_offset.setValue(self._widget.calibration.offset_db)

    def saveState(self, settings):
        settings.setValue("Min", self.spinBox_specmin.value())
        settings.setValue("Max", self.spinBox_specmax.value())
        settings.setValue("RespTime", self.spinBox_resptime.value())
        settings.setValue("TimeMax", self.spinBox_timemax.value())
        settings.setValue("offsetDb", self.doubleSpinBox_offset.value())
        settings.setValue("unitLabel", self.comboBox_unit.currentText())
        settings.setValue("referenceNote", self.lineEdit_reference.text())

    def restoreState(self, settings):
        colorMin = settings.value("Min", DEFAULT_LEVEL_MIN, type=int)
        self.spinBox_specmin.setValue(colorMin)
        colorMax = settings.value("Max", DEFAULT_LEVEL_MAX, type=int)
        self.spinBox_specmax.setValue(colorMax)
        resptime = settings.value("RespTime", DEFAULT_RESPONSE_TIME, type=int)
        self.spinBox_resptime.setValue(resptime)
        timemax = settings.value("TimeMax", DEFAULT_MAXTIME, type=int)
        self.spinBox_timemax.setValue(timemax)
        self.doubleSpinBox_offset.setValue(
            settings.value("offsetDb", DEFAULT_CALIBRATION_OFFSET_DB, type=float)
        )
        unit = settings.value("unitLabel", DEFAULT_UNIT_LABEL, type=str)
        if unit in UNIT_PRESETS:
            self.comboBox_unit.setCurrentText(unit)
        self.lineEdit_reference.setText(
            settings.value("referenceNote", "", type=str)
        )
