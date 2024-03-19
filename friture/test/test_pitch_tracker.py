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

from friture.pitch_tracker import *
from friture.ringbuffer import RingBuffer

class PitchTrackerTest(unittest.TestCase):
    def test_new_frames(self):
        buf = RingBuffer()
        tracker = PitchTracker(buf, fft_size=4, overlap=0.5)
        buf.push(np.array([np.arange(2)]))
        buf.push(np.array([np.arange(2, 5)]))
        npt.assert_array_equal(
            [np.array([np.arange(4)])],
            list(tracker.new_frames())
        )
        buf.push(np.array([np.arange(5, 8)]))
        npt.assert_array_equal(
            [np.array([np.arange(2, 6)]), np.array([np.arange(4, 8)])],
            list(tracker.new_frames())
        )

    def test_estimate_pitch(self):
        buf = RingBuffer()
        tracker = PitchTracker(buf, fft_size=32, overlap=0.5)
        # use inverse fft to synthesize a signal where the first harmonic has
        # higher amplitude than the fundamental:
        pitch = tracker.estimate_pitch(np.array([
            np.fft.irfft(
                [0, 0, .5, 0,  .7, 0, .4, 0,  .2, 0, 0, 0,  0, 0, 0, 0,  0 ],
            )
        ]))
        self.assertEqual(pitch, 3000)

    def test_update(self):
        buf = RingBuffer()
        tracker = PitchTracker(buf, fft_size=32, overlap=0.5, sample_rate=32)

        buf.push(np.array([np.sin(np.linspace(0, 2*np.pi, 32))]))
        npt.assert_array_equal(tracker.get_estimates(1.0), np.zeros((3,)))
        self.assertTrue(tracker.update())
        self.assertFalse(tracker.update())
        npt.assert_array_equal(tracker.get_estimates(1.0), [0, 0, 1500])

        buf.push(np.array([np.sin(np.linspace(0, 4*np.pi, 32))]))
        self.assertTrue(tracker.update())
        self.assertFalse(tracker.update())
        # spectral leakage and low resolution mean this doesn't correctly
        # pick up the doubled pitch in the second half of the signal :/
        npt.assert_array_equal(
            tracker.get_estimates(2.0), [0, 0, 1500, 1500, 1500]
        )
