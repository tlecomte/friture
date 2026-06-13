#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""IEC-style A/B/C frequency weighting for time-domain level meters."""

from __future__ import annotations

import numpy as np

from friture.audiobackend import SAMPLING_RATE
from friture_extensions.lfilter import pyx_lfilter_float64_1D

WEIGHTING_NONE = 0
WEIGHTING_A = 1
WEIGHTING_B = 2
WEIGHTING_C = 3
DEFAULT_WEIGHTING = WEIGHTING_NONE

WEIGHTING_NAMES = ("None", "A", "B", "C")

# Biquad sections (b, a) for 48 kHz, from matched-z A/B/C design (MIT, sound_weighting_filters).
_WEIGHTING_BIQUADS = {
    WEIGHTING_A: (
        (
            np.array([0.7545506848211173, 0.0, 0.0]),
            np.array([1.0, -0.4053225490428304, 0.04107159219064441]),
        ),
        (
            np.array([1.0, -2.0, 1.0]),
            np.array([1.0, -1.8939389909436022, 0.8952272888746267]),
        ),
        (
            np.array([1.0, -2.0, 1.0]),
            np.array([1.0, -1.9946144592366002, 0.9946217102489288]),
        ),
    ),
    WEIGHTING_B: (
        (
            np.array([0.6390744656351163, 0.0, 0.0]),
            np.array([1.0, -0.2026612745214152, 0.0]),
        ),
        (
            np.array([1.0, -1.0, 0.0]),
            np.array([1.0, -1.1821287930983142, 0.19850013566712227]),
        ),
        (
            np.array([1.0, -2.0, 1.0]),
            np.array([1.0, -1.9946144592366002, 0.9946217102489288]),
        ),
    ),
    WEIGHTING_C: (
        (
            np.array([0.6377662580605287, 0.0, 0.0]),
            np.array([1.0, -0.4053225490428304, 0.04107159219064441]),
        ),
        (
            np.array([1.0, -2.0, 1.0]),
            np.array([1.0, -1.9946144592366002, 0.9946217102489288]),
        ),
    ),
}


def weighting_suffix(weighting: int) -> str:
    if weighting == WEIGHTING_NONE:
        return ""
    if 0 <= weighting < len(WEIGHTING_NAMES):
        return f" ({WEIGHTING_NAMES[weighting]})"
    return ""


def _empty_filter_state() -> list[np.ndarray]:
    return []


def _make_filter_state(weighting: int) -> list[np.ndarray]:
    sections = _WEIGHTING_BIQUADS.get(weighting, ())
    return [np.zeros(len(b) - 1) for b, _a in sections]


class WeightingFilter:
    def __init__(self) -> None:
        self.weighting = DEFAULT_WEIGHTING
        self._state_ch1 = _empty_filter_state()
        self._state_ch2 = _empty_filter_state()

    def set_weighting(self, weighting: int) -> None:
        if weighting not in _WEIGHTING_BIQUADS and weighting != WEIGHTING_NONE:
            weighting = DEFAULT_WEIGHTING
        if weighting == self.weighting:
            return
        self.weighting = weighting
        self.reset()

    def reset(self) -> None:
        if self.weighting == WEIGHTING_NONE:
            self._state_ch1 = _empty_filter_state()
            self._state_ch2 = _empty_filter_state()
            return
        state = _make_filter_state(self.weighting)
        self._state_ch1 = [zi.copy() for zi in state]
        self._state_ch2 = [zi.copy() for zi in state]

    def apply(self, samples: np.ndarray, channel: int) -> np.ndarray:
        if self.weighting == WEIGHTING_NONE or samples.size == 0:
            return samples

        if SAMPLING_RATE != 48000:
            return samples

        state = self._state_ch1 if channel == 1 else self._state_ch2
        output = np.ascontiguousarray(samples, dtype=np.float64)
        for index, (b, a) in enumerate(_WEIGHTING_BIQUADS[self.weighting]):
            output, state[index] = pyx_lfilter_float64_1D(b, a, output, state[index])
        return output
