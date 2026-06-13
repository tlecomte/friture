#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Apply global scalar + mic cal-file correction to frequency-domain dB values."""

from __future__ import annotations

import numpy as np
from numpy import float64

from friture.level_calibration import find_global_calibration
from friture.mic_cal_file import MicCalFile


def frequency_adjustment_db(
    frequencies_hz: np.ndarray,
    *,
    offset_db: float = 0.0,
    mic_cal: MicCalFile | None = None,
) -> np.ndarray:
    """Return dB values to add to raw spectrum/octave bins for calibrated display."""
    freqs = np.asarray(frequencies_hz, dtype=float64)
    adjustment = np.full(freqs.shape, offset_db, dtype=float64)
    if mic_cal is not None and mic_cal.has_frequency_data:
        adjustment -= mic_cal.interpolate_db(freqs)
    return adjustment


def scalar_offset_db_for_owner(owner) -> float:
    service = find_global_calibration(owner)
    if service is None:
        return 0.0
    return float(service.calibration.offset_db)


def mic_frequency_adjustment_db_for_owner(
    owner,
    frequencies_hz: np.ndarray,
) -> np.ndarray:
    """Frequency-dependent mic cal correction only (no scalar level offset)."""
    service = find_global_calibration(owner)
    if service is None:
        return np.zeros(len(frequencies_hz), dtype=float64)
    return frequency_adjustment_db(
        frequencies_hz,
        offset_db=0.0,
        mic_cal=service.mic_cal,
    )


def calibrated_spec_range(
    base_min: float, base_max: float, owner
) -> tuple[float, float]:
    """Shift user display limits by the global scalar calibration offset."""
    offset = scalar_offset_db_for_owner(owner)
    return base_min + offset, base_max + offset


def frequency_adjustment_db_for_owner(
    owner,
    frequencies_hz: np.ndarray,
) -> np.ndarray:
    service = find_global_calibration(owner)
    if service is None:
        return np.zeros(len(frequencies_hz), dtype=float64)
    return service.frequency_adjustment_db(frequencies_hz)
