#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Mixin for widgets that support global calibration with optional local override."""

from __future__ import annotations

from friture.level_calibration import (
    LevelCalibration,
    find_global_calibration,
    read_settings_float,
    resolve_calibration,
    write_settings_float,
)


class CalibrationOverrideMixin:
    def init_calibration_override(self, owner) -> None:
        self._global_calibration = find_global_calibration(owner)
        self.use_global_calibration = True
        self.local_calibration = LevelCalibration()
        if self._global_calibration is not None:
            self._global_calibration.changed.connect(self._global_calibration_changed)

    def effective_calibration(self) -> LevelCalibration:
        global_cal = (
            self._global_calibration.calibration
            if self._global_calibration is not None
            else LevelCalibration()
        )
        return resolve_calibration(
            global_cal,
            self.local_calibration,
            self.use_global_calibration,
        )

    def set_use_global_calibration(self, use_global: bool) -> None:
        if self.use_global_calibration != use_global:
            self.use_global_calibration = use_global
            self.on_effective_calibration_changed()

    def set_local_calibration_offset(self, offset_db: float) -> None:
        self.local_calibration.offset_db = offset_db
        if not self.use_global_calibration:
            self.on_effective_calibration_changed()

    def set_local_unit_label(self, unit_label: str) -> None:
        self.local_calibration.unit_label = unit_label
        if not self.use_global_calibration:
            self.on_effective_calibration_changed()

    def set_local_reference_note(self, note: str) -> None:
        self.local_calibration.reference_note = note

    def calibrate_local_to_target(self, raw_rms_db: float, target_db: float) -> None:
        from friture.level_calibration import calibration_offset_for_target

        self.local_calibration.offset_db = calibration_offset_for_target(
            raw_rms_db, target_db
        )
        if not self.use_global_calibration:
            self.on_effective_calibration_changed()

    def _global_calibration_changed(self) -> None:
        if self.use_global_calibration:
            self.on_effective_calibration_changed()

    def on_effective_calibration_changed(self) -> None:
        """Subclasses refresh labels/plots when effective calibration changes."""

    def restore_calibration_override_state(self, settings) -> None:
        if settings.contains("useGlobalCalibration"):
            self.use_global_calibration = settings.value(
                "useGlobalCalibration", True, type=bool
            )
        elif settings.contains("offsetDb"):
            offset = read_settings_float(settings, "offsetDb", 0.0)
            self.use_global_calibration = offset == 0.0

        self.local_calibration.offset_db = read_settings_float(
            settings, "offsetDb", self.local_calibration.offset_db
        )
        self.local_calibration.unit_label = settings.value(
            "unitLabel", self.local_calibration.unit_label, type=str
        )
        self.local_calibration.reference_note = settings.value(
            "referenceNote", self.local_calibration.reference_note, type=str
        )

    def save_calibration_override_state(self, settings) -> None:
        settings.setValue("useGlobalCalibration", self.use_global_calibration)
        write_settings_float(settings, "offsetDb", self.local_calibration.offset_db)
        settings.setValue("unitLabel", self.local_calibration.unit_label)
        settings.setValue("referenceNote", self.local_calibration.reference_note)
