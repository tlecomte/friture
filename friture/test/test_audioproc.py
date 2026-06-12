# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

import unittest

import numpy as np
import numpy.testing as npt

from friture.audiobackend import SAMPLING_RATE
from friture.audioproc import audioproc


class AudioprocTest(unittest.TestCase):
    def test_set_fftsize_updates_window_and_frequency_bins(self) -> None:
        proc = audioproc()
        proc.set_fftsize(1024)

        self.assertEqual(proc.fft_size, 1024)
        self.assertEqual(len(proc.window), 1024)
        self.assertEqual(len(proc.get_freq_scale()), 513)
        npt.assert_array_almost_equal(proc.get_freq_scale()[0], 0.0)
        npt.assert_array_almost_equal(proc.get_freq_scale()[-1], SAMPLING_RATE / 2)

    def test_analyzelive_returns_normalized_power_spectrum(self) -> None:
        proc = audioproc()
        proc.set_fftsize(256)
        samples = np.ones(256)

        spectrum = proc.analyzelive(samples)

        self.assertEqual(spectrum.shape, (129,))
        self.assertGreater(spectrum[0], 0.0)

    def test_norm_square_divides_by_fft_size_squared(self) -> None:
        proc = audioproc()
        proc.set_fftsize(4)
        fft = np.array([4 + 0j, 0 + 0j, 0 + 0j])

        spectrum = proc.norm_square(fft)

        npt.assert_array_almost_equal(spectrum, [1.0, 0.0, 0.0])
