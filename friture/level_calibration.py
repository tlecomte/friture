#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Map raw digital dB readings to user-calibrated display values."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DEFAULT_UNIT_LABEL = "dB FS"
DEFAULT_OFFSET_DB = 0.0

UNIT_PRESETS = ["dB FS", "dBSPL", "dBu", "dB"]


def unit_label_for_calibration_target(unit_label: str, target_db: float) -> str:
    """Pick a sensible display unit when calibrating from a digital default."""
    if unit_label not in ("dB FS", "dBFS", "dB"):
        return unit_label
    if target_db >= 40.0:
        return "dBSPL"
    if target_db <= -30.0:
        return "dBu"
    return unit_label


def python_float(value) -> float:
    """Coerce numeric values (including numpy scalars) to plain Python float."""
    return float(value)


def read_settings_float(settings, key: str, default: float) -> float:
    """Read a float from QSettings, including legacy numpy scalar values."""
    if not settings.contains(key):
        return default
    value = settings.value(key, default)
    if value is None:
        return default
    try:
        return python_float(value)
    except (TypeError, ValueError):
        return default


def write_settings_float(settings, key: str, value: float) -> None:
    settings.setValue(key, python_float(value))


@dataclass
class LevelCalibration:
    offset_db: float = DEFAULT_OFFSET_DB
    unit_label: str = DEFAULT_UNIT_LABEL
    reference_note: str = ""


def apply_calibration(raw_db, offset_db: float):
    """Map raw dB reading(s) to calibrated display value(s)."""
    offset = python_float(offset_db)
    if isinstance(raw_db, np.ndarray):
        return np.asarray(raw_db, dtype=float) + offset
    return python_float(raw_db) + offset


def calibration_offset_for_target(raw_db: float, target_db: float) -> float:
    """Return offset so ``apply_calibration(raw_db, offset) == target_db``."""
    return python_float(target_db) - python_float(raw_db)


def resolve_calibration(
    global_calibration: LevelCalibration,
    local_calibration: LevelCalibration,
    use_global: bool,
) -> LevelCalibration:
    if use_global:
        return global_calibration
    return local_calibration


def find_global_calibration(owner) -> "GlobalCalibrationService | None":
    from friture.global_calibration import GlobalCalibrationService

    obj = owner
    while obj is not None:
        if isinstance(obj, GlobalCalibrationService):
            return obj
        calibration = getattr(obj, "global_calibration", None)
        if isinstance(calibration, GlobalCalibrationService):
            return calibration
        obj = obj.parent()
    return None
