# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

import numpy as np

from friture.audiobackend import SAMPLING_RATE
from friture.freq_weighting import (
    WEIGHTING_A,
    WEIGHTING_C,
    WEIGHTING_NONE,
    WeightingFilter,
    weighting_suffix,
)
from friture.level_meter import LevelMeterProcessor
from friture.level_view_model import LevelViewModel
from friture.level_calibration import LevelCalibration
from friture.test.helpers import AudioHarness


class WeightingSuffixTest(unittest.TestCase):
    def test_none_is_empty(self) -> None:
        self.assertEqual(weighting_suffix(WEIGHTING_NONE), "")

    def test_a_suffix(self) -> None:
        self.assertEqual(weighting_suffix(WEIGHTING_A), " (A)")


class WeightingFilterTest(unittest.TestCase):
    def test_a_weighting_attenuates_low_frequency_tone(self) -> None:
        if SAMPLING_RATE != 48000:
            self.skipTest("weighting biquads defined for 48 kHz only")

        harness = AudioHarness()
        low = harness.push_sine(100.0, 8192, amplitude=0.5)
        mid = harness.push_sine(1000.0, 8192, amplitude=0.5)

        flat = LevelMeterProcessor()
        flat.set_weighting(WEIGHTING_NONE)
        weighted = LevelMeterProcessor()
        weighted.set_weighting(WEIGHTING_A)
        view_flat = LevelViewModel()
        view_weighted = LevelViewModel()
        calibration = LevelCalibration()

        flat.handle_new_data(low, view_flat, calibration)
        weighted.handle_new_data(low, view_weighted, calibration)
        low_flat = view_flat.level_data.level_rms
        low_a = view_weighted.level_data.level_rms

        flat.handle_new_data(mid, view_flat, calibration)
        weighted.handle_new_data(mid, view_weighted, calibration)
        mid_flat = view_flat.level_data.level_rms
        mid_a = view_weighted.level_data.level_rms

        self.assertLess(low_a, low_flat - 15.0)
        self.assertAlmostEqual(mid_a, mid_flat, delta=2.0)

    def test_c_is_closer_to_flat_at_midband_than_a(self) -> None:
        if SAMPLING_RATE != 48000:
            self.skipTest("weighting biquads defined for 48 kHz only")

        harness = AudioHarness()
        tone = harness.push_sine(1000.0, 8192, amplitude=0.5)

        flat = LevelMeterProcessor()
        flat.set_weighting(WEIGHTING_NONE)
        c_meter = LevelMeterProcessor()
        c_meter.set_weighting(WEIGHTING_C)
        calibration = LevelCalibration()

        view_flat = LevelViewModel()
        view_c = LevelViewModel()

        flat.handle_new_data(tone, view_flat, calibration)
        c_meter.handle_new_data(tone, view_c, calibration)

        flat_reading = view_flat.level_data.level_rms
        c_delta = abs(view_c.level_data.level_rms - flat_reading)

        self.assertLess(c_delta, 1.0)

    def test_filter_state_resets_on_weighting_change(self) -> None:
        filt = WeightingFilter()
        filt.set_weighting(WEIGHTING_A)
        samples = np.ones(64, dtype=np.float64)
        filt.apply(samples, channel=1)
        a_state_len = len(filt._state_ch1)  # noqa: SLF001
        filt.set_weighting(WEIGHTING_C)
        self.assertNotEqual(len(filt._state_ch1), a_state_len)  # noqa: SLF001
