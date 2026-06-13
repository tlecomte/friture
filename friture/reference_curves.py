#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Reference target curves for FFT and octave spectrum overlays."""

from __future__ import annotations

import numpy as np

REFERENCE_NONE = 0
REFERENCE_FLAT = 1
REFERENCE_PINK = 2
REFERENCE_A_WEIGHT = 3
REFERENCE_HOUSE = 4

REFERENCE_PRESET_NAMES = ("None", "Flat", "Pink", "A-weighting", "House")
DEFAULT_REFERENCE_PRESET = REFERENCE_NONE
DEFAULT_REFERENCE_OFFSET_DB = 0.0
DEFAULT_ANCHOR_FREQ_HZ = 1000.0
HOUSE_ROLLOFF_START_HZ = 2000.0


def a_weighting_db(frequencies_hz: np.ndarray) -> np.ndarray:
    """Same A-weighting curve as ``audioproc.update_freq_cache`` (dB)."""
    f = np.asarray(frequencies_hz, dtype=float)
    f2 = f * f
    ra = (
        12200.0**2
        * f2
        * f2
        / (
            (f2 + 20.6**2)
            * (f2 + 12200.0**2)
            * np.sqrt(f2 + 107.7**2)
            * np.sqrt(f2 + 737.9**2)
        )
    )
    return 2.0 + 20.0 * np.log10(ra + 1e-50)


def _pink_fft_db(
    frequencies_hz: np.ndarray, anchor_freq_hz: float
) -> np.ndarray:
    freqs = np.maximum(np.asarray(frequencies_hz, dtype=float), 1e-20)
    anchor = max(anchor_freq_hz, 1e-20)
    return -10.0 * np.log10(freqs / anchor)


def _house_db(frequencies_hz: np.ndarray) -> np.ndarray:
    freqs = np.asarray(frequencies_hz, dtype=float)
    values = np.zeros_like(freqs)
    above = freqs > HOUSE_ROLLOFF_START_HZ
    values[above] = -10.0 * np.log10(freqs[above] / HOUSE_ROLLOFF_START_HZ)
    return values


def reference_curve_db(
    preset: int,
    frequencies_hz: np.ndarray,
    *,
    offset_db: float = DEFAULT_REFERENCE_OFFSET_DB,
    anchor_freq_hz: float = DEFAULT_ANCHOR_FREQ_HZ,
    display_mode: str = "fft",
) -> np.ndarray | None:
    """Return dB target values aligned with the plot Y axis, or None if hidden."""
    if preset == REFERENCE_NONE:
        return None

    freqs = np.asarray(frequencies_hz, dtype=float)
    if freqs.size == 0:
        return np.array([], dtype=float)

    if preset == REFERENCE_FLAT:
        values = np.zeros_like(freqs)
    elif preset == REFERENCE_PINK:
        if display_mode == "octave":
            values = np.zeros_like(freqs)
        else:
            values = _pink_fft_db(freqs, anchor_freq_hz)
    elif preset == REFERENCE_A_WEIGHT:
        values = a_weighting_db(freqs)
        values -= float(a_weighting_db(np.array([anchor_freq_hz]))[0])
    elif preset == REFERENCE_HOUSE:
        values = _house_db(freqs)
    else:
        return None

    return values + float(offset_db)


def reference_overlay_label(preset: int, offset_db: float) -> str:
    if preset == REFERENCE_NONE:
        return ""
    name = REFERENCE_PRESET_NAMES[preset]
    if abs(offset_db) < 0.05:
        return f"Target: {name}"
    return f"Target: {name} {offset_db:+.1f} dB"
