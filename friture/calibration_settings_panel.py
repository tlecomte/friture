#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Shared calibration form rows for settings and dock dialogs."""

from __future__ import annotations

from PyQt5 import QtWidgets

from friture.level_calibration import DEFAULT_OFFSET_DB, DEFAULT_UNIT_LABEL, UNIT_PRESETS


class CalibrationFormRows:
    def __init__(
        self,
        form_layout: QtWidgets.QFormLayout,
        *,
        include_use_global: bool = False,
        include_calibrate: bool = True,
    ) -> None:
        self._fields: list[QtWidgets.QWidget] = []

        if include_use_global:
            self.checkBox_use_global = QtWidgets.QCheckBox("Use global calibration")
            self.checkBox_use_global.setChecked(True)
            form_layout.addRow(self.checkBox_use_global)
        else:
            self.checkBox_use_global = None

        self.doubleSpinBox_offset = QtWidgets.QDoubleSpinBox()
        self.doubleSpinBox_offset.setDecimals(1)
        self.doubleSpinBox_offset.setRange(-500.0, 500.0)
        self.doubleSpinBox_offset.setValue(DEFAULT_OFFSET_DB)
        self.doubleSpinBox_offset.setSuffix(" dB")

        self.comboBox_unit = QtWidgets.QComboBox()
        for unit in UNIT_PRESETS:
            self.comboBox_unit.addItem(unit)
        self.comboBox_unit.setCurrentText(DEFAULT_UNIT_LABEL)

        self.lineEdit_reference = QtWidgets.QLineEdit()
        self.lineEdit_reference.setPlaceholderText("Optional calibration note")

        self.button_calibrate = None
        if include_calibrate:
            self.button_calibrate = QtWidgets.QPushButton(
                "Calibrate from current reading…"
            )

        form_layout.addRow("Calibration offset:", self.doubleSpinBox_offset)
        form_layout.addRow("Unit label:", self.comboBox_unit)
        form_layout.addRow("Reference note:", self.lineEdit_reference)
        if self.button_calibrate is not None:
            form_layout.addRow("", self.button_calibrate)

        self._fields = [
            self.doubleSpinBox_offset,
            self.comboBox_unit,
            self.lineEdit_reference,
        ]
        if self.button_calibrate is not None:
            self._fields.append(self.button_calibrate)

        if self.checkBox_use_global is not None:
            self.checkBox_use_global.toggled.connect(self._sync_enabled_state)
            self._sync_enabled_state(self.checkBox_use_global.isChecked())

    def _sync_enabled_state(self, use_global: bool) -> None:
        for field in self._fields:
            field.setEnabled(not use_global)

    def set_use_global(self, use_global: bool) -> None:
        if self.checkBox_use_global is not None:
            self.checkBox_use_global.setChecked(use_global)

    def use_global(self) -> bool:
        if self.checkBox_use_global is None:
            return True
        return self.checkBox_use_global.isChecked()

    def load(self, offset_db: float, unit_label: str, reference_note: str) -> None:
        self.doubleSpinBox_offset.blockSignals(True)
        self.comboBox_unit.blockSignals(True)
        self.lineEdit_reference.blockSignals(True)
        self.doubleSpinBox_offset.setValue(offset_db)
        if unit_label in UNIT_PRESETS:
            self.comboBox_unit.setCurrentText(unit_label)
        self.lineEdit_reference.setText(reference_note)
        self.doubleSpinBox_offset.blockSignals(False)
        self.comboBox_unit.blockSignals(False)
        self.lineEdit_reference.blockSignals(False)

    def save(self) -> tuple[float, str, str]:
        return (
            self.doubleSpinBox_offset.value(),
            self.comboBox_unit.currentText(),
            self.lineEdit_reference.text(),
        )
