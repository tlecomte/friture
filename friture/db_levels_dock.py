#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Dock widget: calibrated peak/RMS dB readout."""

from PyQt5.QtCore import QSettings, QObject

from friture.db_levels_settings import DbLevels_Settings_Dialog
from friture.freq_weighting import DEFAULT_WEIGHTING, weighting_suffix
from friture.level_calibration import (
    LevelCalibration,
    calibration_offset_for_target,
)
from friture.level_meter import LevelMeterProcessor
from friture.level_view_model import LevelViewModel


class DbLevelsDockWidget(QObject):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self._parent = parent
        self.audiobuffer = None
        self._level_view_model = LevelViewModel(self)
        self.calibration = LevelCalibration()
        self._meter = LevelMeterProcessor()
        self._sync_view_model_calibration()
        self.settings_dialog = DbLevels_Settings_Dialog(parent, self)

    def _sync_view_model_calibration(self) -> None:
        self._level_view_model.unit_label = self.calibration.unit_label

    def _sync_view_model_weighting(self) -> None:
        self._level_view_model.weighting_suffix = weighting_suffix(self._meter.weighting())

    def set_buffer(self, buffer) -> None:
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata) -> None:
        self._meter.handle_new_data(floatdata, self._level_view_model, self.calibration)

    def canvasUpdate(self) -> None:
        self._meter.canvas_update(self._level_view_model, self._parent.isVisible())

    def pause(self) -> None:
        pass

    def restart(self) -> None:
        pass

    def settings_called(self, checked) -> None:
        del checked
        self.settings_dialog.show()

    def set_calibration_offset(self, offset_db: float) -> None:
        self.calibration.offset_db = offset_db

    def set_unit_label(self, unit_label: str) -> None:
        self.calibration.unit_label = unit_label
        self._sync_view_model_calibration()

    def set_reference_note(self, note: str) -> None:
        self.calibration.reference_note = note

    def set_response_time_s(self, response_time_s: float) -> None:
        self._meter.set_response_time_s(response_time_s)

    def set_weighting(self, weighting: int) -> None:
        self._meter.set_weighting(weighting)
        self._sync_view_model_weighting()

    def calibrate_to_target(self, target_db: float) -> None:
        self.calibration.offset_db = calibration_offset_for_target(
            self._meter.last_raw_rms_db, target_db
        )

    def saveState(self, settings: QSettings) -> None:
        settings.setValue("offsetDb", self.calibration.offset_db)
        settings.setValue("unitLabel", self.calibration.unit_label)
        settings.setValue("referenceNote", self.calibration.reference_note)
        settings.setValue("responseTimeS", self._meter.response_time_s)
        settings.setValue("weighting", self._meter.weighting())

    def restoreState(self, settings: QSettings) -> None:
        self.settings_dialog.restoreState(settings)
        self.calibration.offset_db = settings.value(
            "offsetDb", self.calibration.offset_db, type=float
        )
        self.calibration.unit_label = settings.value(
            "unitLabel", self.calibration.unit_label, type=str
        )
        self.calibration.reference_note = settings.value(
            "referenceNote", self.calibration.reference_note, type=str
        )
        self._meter.set_response_time_s(
            settings.value("responseTimeS", self._meter.response_time_s, type=float)
        )
        self.set_weighting(settings.value("weighting", DEFAULT_WEIGHTING, type=int))
        self._sync_view_model_calibration()

    def qml_file_name(self) -> str:
        return "DbLevelsDock.qml"

    def view_model(self) -> LevelViewModel:
        return self._level_view_model
