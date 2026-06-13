#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Map raw digital dB readings to user-calibrated display values."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_UNIT_LABEL = "dB FS"
DEFAULT_OFFSET_DB = 0.0

UNIT_PRESETS = ["dB FS", "dBSPL", "dBu", "dB"]


@dataclass
class LevelCalibration:
    offset_db: float = DEFAULT_OFFSET_DB
    unit_label: str = DEFAULT_UNIT_LABEL
    reference_note: str = ""


def apply_calibration(raw_db: float, offset_db: float) -> float:
    return raw_db + offset_db


def calibration_offset_for_target(raw_db: float, target_db: float) -> float:
    """Return offset so ``apply_calibration(raw_db, offset) == target_db``."""
    return target_db - raw_db
