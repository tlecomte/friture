# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

import numpy as np

from friture.reference_curves import (
    DEFAULT_REFERENCE_OFFSET_DB,
    REFERENCE_A_WEIGHT,
    REFERENCE_FLAT,
    REFERENCE_HOUSE,
    REFERENCE_NONE,
    REFERENCE_PINK,
    REFERENCE_PRESET_NAMES,
    a_weighting_db,
    reference_curve_db,
)


class ReferenceCurvesTest(unittest.TestCase):
    def test_none_returns_none(self) -> None:
        freqs = np.array([100.0, 1000.0, 10000.0])

        self.assertIsNone(reference_curve_db(REFERENCE_NONE, freqs))

    def test_flat_is_zero_before_offset(self) -> None:
        freqs = np.array([50.0, 1000.0, 20000.0])

        curve = reference_curve_db(REFERENCE_FLAT, freqs, display_mode="fft")

        np.testing.assert_allclose(curve, [0.0, 0.0, 0.0])

    def test_offset_shifts_curve(self) -> None:
        freqs = np.array([1000.0])

        curve = reference_curve_db(
            REFERENCE_FLAT,
            freqs,
            offset_db=12.5,
            display_mode="octave",
        )

        self.assertAlmostEqual(curve[0], 12.5)

    def test_pink_fft_falls_with_frequency(self) -> None:
        freqs = np.array([100.0, 1000.0, 10000.0])

        curve = reference_curve_db(REFERENCE_PINK, freqs, display_mode="fft")

        self.assertAlmostEqual(curve[1], 0.0, places=1)
        self.assertGreater(curve[0], curve[1])
        self.assertLess(curve[2], curve[1])
        self.assertAlmostEqual(curve[0] - curve[2], 20.0, delta=0.5)

    def test_pink_octave_is_flat(self) -> None:
        freqs = np.array([125.0, 1000.0, 8000.0])

        curve = reference_curve_db(REFERENCE_PINK, freqs, display_mode="octave")

        np.testing.assert_allclose(curve, [0.0, 0.0, 0.0])

    def test_a_weighting_anchored_at_one_khz(self) -> None:
        freqs = np.array([100.0, 1000.0, 10000.0])

        curve = reference_curve_db(REFERENCE_A_WEIGHT, freqs, display_mode="fft")

        self.assertAlmostEqual(curve[1], 0.0, places=1)
        self.assertLess(curve[0], curve[1])
        self.assertLess(curve[2], curve[1])

    def test_house_rolls_off_above_two_khz(self) -> None:
        freqs = np.array([1000.0, 2000.0, 4000.0, 8000.0])

        curve = reference_curve_db(REFERENCE_HOUSE, freqs, display_mode="fft")

        self.assertAlmostEqual(curve[0], 0.0)
        self.assertAlmostEqual(curve[1], 0.0)
        self.assertLess(curve[2], 0.0)
        self.assertLess(curve[3], curve[2])

    def test_a_weighting_matches_audioproc_formula(self) -> None:
        freqs = np.array([500.0, 1000.0, 2000.0])
        ra = (
            12200.0**2
            * freqs**4
            / (
                (freqs**2 + 20.6**2)
                * (freqs**2 + 12200.0**2)
                * np.sqrt(freqs**2 + 107.7**2)
                * np.sqrt(freqs**2 + 737.9**2)
            )
        )
        expected = 2.0 + 20.0 * np.log10(ra + 1e-50)

        np.testing.assert_allclose(a_weighting_db(freqs), expected)

    def test_preset_names_cover_all_presets(self) -> None:
        self.assertEqual(len(REFERENCE_PRESET_NAMES), 5)
        self.assertEqual(DEFAULT_REFERENCE_OFFSET_DB, 0.0)
