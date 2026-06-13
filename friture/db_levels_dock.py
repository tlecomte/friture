#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Dock widget: calibrated peak/RMS dB readout."""

from PyQt5.QtCore import QSettings, QObject

from friture.calibration_override import CalibrationOverrideMixin
from friture.db_levels_settings import DbLevels_Settings_Dialog
from friture.freq_weighting import DEFAULT_WEIGHTING, weighting_suffix
from friture.level_meter import LevelMeterProcessor, calibration_raw_rms_db
from friture.level_view_model import LevelViewModel


class DbLevelsDockWidget(QObject, CalibrationOverrideMixin):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self._parent = parent
        self.init_calibration_override(parent)
        self.audiobuffer = None
        self._level_view_model = LevelViewModel(self)
        self._meter = LevelMeterProcessor()
        self._sync_view_model_weighting()
        self.on_effective_calibration_changed()
        self.settings_dialog = DbLevels_Settings_Dialog(parent, self)

    def on_effective_calibration_changed(self) -> None:
        self._level_view_model.unit_label = self.effective_calibration().unit_label

    def set_buffer(self, buffer) -> None:
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata) -> None:
        self._meter.handle_new_data(
            floatdata, self._level_view_model, self.effective_calibration()
        )

    def canvasUpdate(self) -> None:
        self._meter.canvas_update(self._level_view_model, self._parent.isVisible())

    def pause(self) -> None:
        pass

    def restart(self) -> None:
        pass

    def settings_called(self, checked) -> None:
        del checked
        self.settings_dialog.sync_from_widget()
        self.settings_dialog.show()

    def set_calibration_offset(self, offset_db: float) -> None:
        self.set_local_calibration_offset(offset_db)

    def set_unit_label(self, unit_label: str) -> None:
        self.set_local_unit_label(unit_label)

    def set_reference_note(self, note: str) -> None:
        self.set_local_reference_note(note)

    def set_response_time_s(self, response_time_s: float) -> None:
        self._meter.set_response_time_s(response_time_s)

    def set_weighting(self, weighting: int) -> None:
        self._meter.set_weighting(weighting)
        self._sync_view_model_weighting()

    def _sync_view_model_weighting(self) -> None:
        self._level_view_model.weighting_suffix = weighting_suffix(self._meter.weighting())

    def calibrate_to_target(self, target_db: float) -> None:
        raw_rms_db = calibration_raw_rms_db(
            self.audiobuffer,
            meter=self._meter,
            weighting=self._meter.weighting(),
        )
        self.calibrate_local_to_target(raw_rms_db, target_db)
        self._meter.reset_smoothing()

    def saveState(self, settings: QSettings) -> None:
        self.save_calibration_override_state(settings)
        settings.setValue("responseTimeS", self._meter.response_time_s)
        settings.setValue("weighting", self._meter.weighting())

    def restoreState(self, settings: QSettings) -> None:
        self.settings_dialog.restoreState(settings)
        self.restore_calibration_override_state(settings)
        self._meter.set_response_time_s(
            settings.value("responseTimeS", self._meter.response_time_s, type=float)
        )
        self.set_weighting(settings.value("weighting", DEFAULT_WEIGHTING, type=int))
        self.on_effective_calibration_changed()

    def qml_file_name(self) -> str:
        return "DbLevelsDock.qml"

    def view_model(self) -> LevelViewModel:
        return self._level_view_model
