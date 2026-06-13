#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

from PyQt5 import QtWidgets

from friture.calibration_settings_panel import CalibrationFormRows
from friture.level_calibration import read_settings_float, unit_label_for_calibration_target, write_settings_float
from friture.level_meter import (
    calibration_quiet_message,
    calibration_raw_rms_db,
    calibration_signal_too_quiet,
)
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

        self.formLayout.addRow("Max:", self.spinBox_specmax)
        self.formLayout.addRow("Min:", self.spinBox_specmin)
        self.formLayout.addRow("Response Time", self.spinBox_resptime)
        self.formLayout.addRow("Time Range:", self.spinBox_timemax)

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

        self.spinBox_specmin.valueChanged.connect(view_model.setmin)
        self.spinBox_specmax.valueChanged.connect(view_model.setmax)
        self.spinBox_resptime.valueChanged.connect(view_model.setresptime)
        self.spinBox_timemax.valueChanged.connect(view_model.setduration)

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
            live_raw_rms_db=self._widget.last_raw_rms_db,
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

    def saveState(self, settings):
        settings.setValue("Min", self.spinBox_specmin.value())
        settings.setValue("Max", self.spinBox_specmax.value())
        settings.setValue("RespTime", self.spinBox_resptime.value())
        settings.setValue("TimeMax", self.spinBox_timemax.value())
        settings.setValue("useGlobalCalibration", self.calibration_rows.use_global())
        offset_db, unit_label, reference_note = self.calibration_rows.save()
        write_settings_float(settings, "offsetDb", offset_db)
        settings.setValue("unitLabel", unit_label)
        settings.setValue("referenceNote", reference_note)

    def restoreState(self, settings):
        colorMin = settings.value("Min", DEFAULT_LEVEL_MIN, type=int)
        self.spinBox_specmin.setValue(colorMin)
        colorMax = settings.value("Max", DEFAULT_LEVEL_MAX, type=int)
        self.spinBox_specmax.setValue(colorMax)
        resptime = settings.value("RespTime", DEFAULT_RESPONSE_TIME, type=int)
        self.spinBox_resptime.setValue(resptime)
        timemax = settings.value("TimeMax", DEFAULT_MAXTIME, type=int)
        self.spinBox_timemax.setValue(timemax)
        self.calibration_rows.set_use_global(
            settings.value("useGlobalCalibration", True, type=bool)
        )
        self.calibration_rows.load(
            read_settings_float(settings, "offsetDb", DEFAULT_CALIBRATION_OFFSET_DB),
            settings.value("unitLabel", DEFAULT_UNIT_LABEL, type=str),
            settings.value("referenceNote", "", type=str),
        )
