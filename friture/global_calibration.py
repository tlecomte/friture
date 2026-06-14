#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""App-wide input level calibration stored in main settings."""

from __future__ import annotations

import os

import numpy as np
from PyQt5.QtCore import QObject, QSettings, pyqtSignal

from friture.level_calibration import (
    DEFAULT_OFFSET_DB,
    DEFAULT_UNIT_LABEL,
    LevelCalibration,
    calibration_offset_for_target,
    python_float,
    read_settings_float,
    write_settings_float,
)
from friture.mic_cal_file import MicCalFile, MicCalFileError, load_mic_cal_file


class GlobalCalibrationService(QObject):
    changed = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.calibration = LevelCalibration()
        self.mic_cal: MicCalFile | None = None
        self.mic_cal_file_path = ""
        self._calibrated_at: str = ""

    def frequency_adjustment_db(self, frequencies_hz) -> "np.ndarray":
        from friture.global_frequency_calibration import frequency_adjustment_db

        return frequency_adjustment_db(
            frequencies_hz,
            offset_db=self.calibration.offset_db,
            mic_cal=self.mic_cal,
        )

    def set_mic_cal_file(self, path: str) -> None:
        path = path.strip()
        if not path:
            self.clear_mic_cal_file()
            return

        absolute_path = os.path.abspath(path)
        if absolute_path == self.mic_cal_file_path and self.mic_cal is not None:
            return

        mic_cal = load_mic_cal_file(absolute_path)
        self.mic_cal = mic_cal
        self.mic_cal_file_path = mic_cal.source_path
        if not self.calibration.reference_note.strip():
            self.calibration.reference_note = mic_cal.summary()
        self.changed.emit()

    def clear_mic_cal_file(self) -> None:
        if self.mic_cal is None and not self.mic_cal_file_path:
            return
        self.mic_cal = None
        self.mic_cal_file_path = ""
        self.changed.emit()

    def try_reload_mic_cal_file(self) -> None:
        if not self.mic_cal_file_path:
            return
        try:
            self.mic_cal = load_mic_cal_file(self.mic_cal_file_path)
        except (MicCalFileError, OSError):
            pass

    def set_offset_db(self, offset_db: float) -> None:
        offset_db = python_float(offset_db)
        if self.calibration.offset_db != offset_db:
            self.calibration.offset_db = offset_db
            self.changed.emit()

    def set_unit_label(self, unit_label: str) -> None:
        if self.calibration.unit_label != unit_label:
            self.calibration.unit_label = unit_label
            self.changed.emit()

    def set_reference_note(self, note: str) -> None:
        if self.calibration.reference_note != note:
            self.calibration.reference_note = note
            self.changed.emit()

    def calibrate_to_target(self, raw_rms_db: float, target_db: float) -> None:
        from datetime import datetime
        self.set_offset_db(calibration_offset_for_target(raw_rms_db, target_db))
        self._calibrated_at = datetime.now().isoformat()

    def _profile_group(self, device_key: str) -> str:
        return f"GlobalCalibration/profiles/{device_key}" if device_key else ""

    def saveState(self, settings: QSettings, device_key: str = "") -> None:
        if device_key:
            settings.beginGroup(self._profile_group(device_key))
        self._write_calibration(settings)
        if device_key:
            settings.endGroup()

    def _write_calibration(self, settings: QSettings) -> None:
        if self._calibrated_at:
            settings.setValue("calibratedAt", self._calibrated_at)
        write_settings_float(settings, "offsetDb", self.calibration.offset_db)
        settings.setValue("unitLabel", self.calibration.unit_label)
        settings.setValue("referenceNote", self.calibration.reference_note)
        settings.setValue("micCalFilePath", self.mic_cal_file_path)
        if self.mic_cal is not None:
            settings.setValue(
                "micCalFrequencies", self.mic_cal.frequencies_hz.tolist()
            )
            settings.setValue(
                "micCalCorrections", self.mic_cal.corrections_db.tolist()
            )
            if self.mic_cal.sensitivity_db is not None:
                write_settings_float(
                    settings, "micCalSensitivityDb", self.mic_cal.sensitivity_db
                )
            else:
                settings.remove("micCalSensitivityDb")
            if self.mic_cal.reference_freq_hz is not None:
                write_settings_float(
                    settings, "micCalReferenceFreqHz", self.mic_cal.reference_freq_hz
                )
            else:
                settings.remove("micCalReferenceFreqHz")
        else:
            settings.remove("micCalFrequencies")
            settings.remove("micCalCorrections")
            settings.remove("micCalSensitivityDb")
            settings.remove("micCalReferenceFreqHz")

    def restoreState(self, settings: QSettings, device_key: str = "") -> None:
        if device_key and settings.contains(f"{self._profile_group(device_key)}/offsetDb"):
            settings.beginGroup(self._profile_group(device_key))
            self._read_calibration(settings)
            settings.endGroup()
        else:
            self._read_calibration(settings)
        self.changed.emit()

    def _read_calibration(self, settings: QSettings) -> None:
        self._calibrated_at = settings.value("calibratedAt", "", type=str)
        self.calibration.offset_db = read_settings_float(
            settings, "offsetDb", DEFAULT_OFFSET_DB
        )
        self.calibration.unit_label = settings.value(
            "unitLabel", DEFAULT_UNIT_LABEL, type=str
        )
        self.calibration.reference_note = settings.value(
            "referenceNote", "", type=str
        )
        self.mic_cal_file_path = settings.value("micCalFilePath", "", type=str)
        self.mic_cal = None
        if self.mic_cal_file_path:
            try:
                self.mic_cal = load_mic_cal_file(self.mic_cal_file_path)
            except (MicCalFileError, OSError):
                self.mic_cal = self._mic_cal_from_settings_cache(settings)
        elif settings.contains("micCalFrequencies"):
            self.mic_cal = self._mic_cal_from_settings_cache(settings)
        write_settings_float(settings, "offsetDb", self.calibration.offset_db)

    @staticmethod
    def _mic_cal_from_settings_cache(settings: QSettings) -> MicCalFile | None:
        frequencies = settings.value("micCalFrequencies", [], type=list)
        corrections = settings.value("micCalCorrections", [], type=list)
        if len(frequencies) < 2 or len(corrections) != len(frequencies):
            return None
        sensitivity = read_settings_float(settings, "micCalSensitivityDb", float("nan"))
        reference_freq = read_settings_float(settings, "micCalReferenceFreqHz", float("nan"))
        return MicCalFile(
            frequencies_hz=np.asarray(frequencies, dtype=float),
            corrections_db=np.asarray(corrections, dtype=float),
            sensitivity_db=None if np.isnan(sensitivity) else sensitivity,
            reference_freq_hz=None if np.isnan(reference_freq) else reference_freq,
            source_path=settings.value("micCalFilePath", "", type=str),
        )
