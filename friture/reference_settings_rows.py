#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Shared reference overlay controls for spectrum settings dialogs."""

from __future__ import annotations

from PyQt5 import QtWidgets

from friture.reference_curves import (
    DEFAULT_REFERENCE_OFFSET_DB,
    DEFAULT_REFERENCE_PRESET,
    REFERENCE_PRESET_NAMES,
)


class ReferenceOverlaySettingsRows:
    def __init__(self, form_layout: QtWidgets.QFormLayout) -> None:
        self.comboBox_reference = QtWidgets.QComboBox()
        for name in REFERENCE_PRESET_NAMES:
            self.comboBox_reference.addItem(name)
        self.comboBox_reference.setCurrentIndex(DEFAULT_REFERENCE_PRESET)

        self.doubleSpinBox_reference_offset = QtWidgets.QDoubleSpinBox()
        self.doubleSpinBox_reference_offset.setDecimals(1)
        self.doubleSpinBox_reference_offset.setRange(-200.0, 200.0)
        self.doubleSpinBox_reference_offset.setSuffix(" dB")
        self.doubleSpinBox_reference_offset.setValue(DEFAULT_REFERENCE_OFFSET_DB)

        form_layout.addRow("Reference overlay:", self.comboBox_reference)
        form_layout.addRow("Overlay offset:", self.doubleSpinBox_reference_offset)

    def preset(self) -> int:
        return self.comboBox_reference.currentIndex()

    def offset_db(self) -> float:
        return float(self.doubleSpinBox_reference_offset.value())

    def load(self, preset: int, offset_db: float) -> None:
        self.comboBox_reference.setCurrentIndex(preset)
        self.doubleSpinBox_reference_offset.setValue(offset_db)

    def save_state(self, settings) -> None:
        settings.setValue("referencePreset", self.preset())
        settings.setValue("referenceOffsetDb", self.offset_db())

    def restore_state(self, settings) -> None:
        preset = settings.value(
            "referencePreset", DEFAULT_REFERENCE_PRESET, type=int
        )
        offset_db = settings.value(
            "referenceOffsetDb", DEFAULT_REFERENCE_OFFSET_DB, type=float
        )
        self.load(preset, offset_db)
