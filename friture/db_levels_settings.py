#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

from PyQt5 import QtWidgets

from friture.calibration_settings_panel import CalibrationFormRows
from friture.freq_weighting import DEFAULT_WEIGHTING, WEIGHTING_NAMES
from friture.level_calibration import (
    DEFAULT_OFFSET_DB,
    DEFAULT_UNIT_LABEL,
    read_settings_float,
    unit_label_for_calibration_target,
    write_settings_float,
)
from friture.level_meter import (
    DEFAULT_RESPONSE_TIME_S,
    calibration_quiet_message,
    calibration_raw_rms_db,
    calibration_signal_too_quiet,
)
from friture.settings_dialog_layout import create_form_layout

UNIT_PRESETS = ["dBSPL", "dBu", "dBFS", "dB"]


class DbLevels_Settings_Dialog(QtWidgets.QDialog):
    def __init__(self, parent, widget) -> None:
        super().__init__(parent)

        self._widget = widget
        self.setWindowTitle("dB levels settings")

        self.formLayout = create_form_layout(self)

        self.calibration_rows = CalibrationFormRows(
            self.formLayout, include_use_global=True
        )
        self.calibration_rows.checkBox_use_global.toggled.connect(
            self._widget.set_use_global_calibration
        )
        self.calibration_rows.doubleSpinBox_offset.valueChanged.connect(
            self._widget.set_calibration_offset
        )
        self.calibration_rows.comboBox_unit.currentTextChanged.connect(
            self._widget.set_unit_label
        )
        self.calibration_rows.lineEdit_reference.textChanged.connect(
            self._widget.set_reference_note
        )
        self.calibration_rows.button_calibrate.clicked.connect(self._calibrate_from_current)

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

        self.formLayout.addRow("Frequency weighting:", self.comboBox_weighting)
        self.formLayout.addRow("RMS response time:", self.doubleSpinBox_response)

        self.comboBox_weighting.currentIndexChanged.connect(self._widget.set_weighting)
        self.doubleSpinBox_response.valueChanged.connect(self._widget.set_response_time_s)

    def sync_from_widget(self) -> None:
        self.calibration_rows.set_use_global(self._widget.use_global_calibration)
        self.calibration_rows.load(
            self._widget.local_calibration.offset_db,
            self._widget.local_calibration.unit_label,
            self._widget.local_calibration.reference_note,
        )

    def _calibrate_from_current(self) -> None:
        raw_rms_db = calibration_raw_rms_db(
            self._widget.audiobuffer,
            meter=self._widget._meter,
            weighting=self._widget._meter.weighting(),
        )
        if calibration_signal_too_quiet(raw_rms_db):
            cal = self._widget.effective_calibration()
            QtWidgets.QMessageBox.warning(
                self,
                "Calibrate level",
                calibration_quiet_message(
                    raw_rms_db,
                    offset_db=cal.offset_db,
                    unit_label=cal.unit_label,
                ),
            )
            return
        target_db, ok = QtWidgets.QInputDialog.getDouble(
            self,
            "Calibrate level",
            f"Raw input is {raw_rms_db:.1f} dBFS.\n"
            "It should read (dB):",
            value=94.0,
            decimals=1,
        )
        if ok:
            unit_label = unit_label_for_calibration_target(
                self._widget.local_calibration.unit_label, target_db
            )
            if unit_label != self._widget.local_calibration.unit_label:
                self._widget.set_local_unit_label(unit_label)
            self._widget.calibrate_local_to_target(raw_rms_db, target_db)
            self.calibration_rows.load(
                self._widget.local_calibration.offset_db,
                self._widget.local_calibration.unit_label,
                self._widget.local_calibration.reference_note,
            )

    def saveState(self, settings) -> None:
        settings.setValue("useGlobalCalibration", self.calibration_rows.use_global())
        offset_db, unit_label, reference_note = self.calibration_rows.save()
        write_settings_float(settings, "offsetDb", offset_db)
        settings.setValue("unitLabel", unit_label)
        settings.setValue("referenceNote", reference_note)
        settings.setValue("responseTimeS", self.doubleSpinBox_response.value())
        settings.setValue("weighting", self.comboBox_weighting.currentIndex())

    def restoreState(self, settings) -> None:
        use_global = settings.value("useGlobalCalibration", True, type=bool)
        self.calibration_rows.set_use_global(use_global)
        self.calibration_rows.load(
            read_settings_float(settings, "offsetDb", DEFAULT_OFFSET_DB),
            settings.value("unitLabel", DEFAULT_UNIT_LABEL, type=str),
            settings.value("referenceNote", "", type=str),
        )
        self.doubleSpinBox_response.setValue(
            settings.value("responseTimeS", DEFAULT_RESPONSE_TIME_S, type=float)
        )
        self.comboBox_weighting.setCurrentIndex(
            settings.value("weighting", DEFAULT_WEIGHTING, type=int)
        )
