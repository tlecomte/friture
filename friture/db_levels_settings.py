#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

from PyQt5 import QtWidgets

from friture.freq_weighting import DEFAULT_WEIGHTING, WEIGHTING_NAMES
from friture.level_calibration import DEFAULT_OFFSET_DB, DEFAULT_UNIT_LABEL
from friture.level_meter import DEFAULT_RESPONSE_TIME_S
from friture.settings_dialog_layout import create_form_layout

UNIT_PRESETS = ["dBSPL", "dBu", "dBFS", "dB"]


class DbLevels_Settings_Dialog(QtWidgets.QDialog):
    def __init__(self, parent, widget) -> None:
        super().__init__(parent)

        self._widget = widget
        self.setWindowTitle("dB levels settings")

        self.formLayout = create_form_layout(self)

        self.doubleSpinBox_offset = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_offset.setDecimals(1)
        self.doubleSpinBox_offset.setRange(-200.0, 200.0)
        self.doubleSpinBox_offset.setValue(DEFAULT_OFFSET_DB)
        self.doubleSpinBox_offset.setSuffix(" dB")

        self.comboBox_unit = QtWidgets.QComboBox(self)
        for unit in UNIT_PRESETS:
            self.comboBox_unit.addItem(unit)
        self.comboBox_unit.setCurrentText(DEFAULT_UNIT_LABEL)

        self.lineEdit_reference = QtWidgets.QLineEdit(self)
        self.lineEdit_reference.setPlaceholderText("Optional calibration note")

        self.doubleSpinBox_response = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_response.setDecimals(2)
        self.doubleSpinBox_response.setMinimum(0.05)
        self.doubleSpinBox_response.setMaximum(5.0)
        self.doubleSpinBox_response.setSingleStep(0.05)
        self.doubleSpinBox_response.setValue(DEFAULT_RESPONSE_TIME_S)
        self.doubleSpinBox_response.setSuffix(" s")

        self.comboBox_weighting = QtWidgets.QComboBox(self)
        for name in WEIGHTING_NAMES:
            self.comboBox_weighting.addItem(name)
        self.comboBox_weighting.setCurrentIndex(DEFAULT_WEIGHTING)

        self.button_calibrate = QtWidgets.QPushButton("Calibrate from current reading…", self)
        self.button_calibrate.clicked.connect(self._calibrate_from_current)

        self.formLayout.addRow("Calibration offset:", self.doubleSpinBox_offset)
        self.formLayout.addRow("Unit label:", self.comboBox_unit)
        self.formLayout.addRow("Frequency weighting:", self.comboBox_weighting)
        self.formLayout.addRow("Reference note:", self.lineEdit_reference)
        self.formLayout.addRow("", self.button_calibrate)
        self.formLayout.addRow("RMS response time:", self.doubleSpinBox_response)

        self.doubleSpinBox_offset.valueChanged.connect(self._widget.set_calibration_offset)
        self.comboBox_unit.currentTextChanged.connect(self._widget.set_unit_label)
        self.comboBox_weighting.currentIndexChanged.connect(self._widget.set_weighting)
        self.lineEdit_reference.textChanged.connect(self._widget.set_reference_note)
        self.doubleSpinBox_response.valueChanged.connect(self._widget.set_response_time_s)

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

    def saveState(self, settings) -> None:
        settings.setValue("offsetDb", self.doubleSpinBox_offset.value())
        settings.setValue("unitLabel", self.comboBox_unit.currentText())
        settings.setValue("referenceNote", self.lineEdit_reference.text())
        settings.setValue("responseTimeS", self.doubleSpinBox_response.value())
        settings.setValue("weighting", self.comboBox_weighting.currentIndex())

    def restoreState(self, settings) -> None:
        self.doubleSpinBox_offset.setValue(
            settings.value("offsetDb", DEFAULT_OFFSET_DB, type=float)
        )
        unit = settings.value("unitLabel", DEFAULT_UNIT_LABEL, type=str)
        if unit in UNIT_PRESETS:
            self.comboBox_unit.setCurrentText(unit)
        self.lineEdit_reference.setText(
            settings.value("referenceNote", "", type=str)
        )
        self.doubleSpinBox_response.setValue(
            settings.value("responseTimeS", DEFAULT_RESPONSE_TIME_S, type=float)
        )
        self.comboBox_weighting.setCurrentIndex(
            settings.value("weighting", DEFAULT_WEIGHTING, type=int)
        )
