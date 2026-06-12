# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

import numpy as np

from friture.filter import NOCTAVE
from friture.octavefilters import Octave_Filters


class OctaveFiltersTest(unittest.TestCase):
    def test_twelve_bands_per_octave_has_expected_width(self) -> None:
        filters = Octave_Filters(12)

        self.assertEqual(filters.nbands, 12 * NOCTAVE)
        self.assertEqual(len(filters.f_nominal), filters.nbands)

    def test_filter_bank_returns_one_band_per_filter(self) -> None:
        filters = Octave_Filters(12)
        samples = np.sin(
            2 * np.pi * 440 * np.linspace(0, 0.25, 12000, endpoint=False),
        )

        bands, _decs = filters.filter(samples)

        self.assertEqual(len(bands), filters.nbands)
        peak = max(float(np.max(np.abs(band))) for band in bands)
        self.assertGreater(peak, 0.0)
