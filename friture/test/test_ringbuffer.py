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
from friture.ringbuffer import RingBuffer


class RingBufferTest(unittest.TestCase):
    def test_push_and_read_back(self) -> None:
        buf = RingBuffer()
        samples = np.arange(256).reshape(1, 256)
        buf.push(samples, input_time=256 / SAMPLING_RATE)
        npt.assert_array_equal(buf.data(256), samples)

    def test_push_empty_chunk(self) -> None:
        buf = RingBuffer()
        samples = np.arange(64).reshape(1, 64)
        buf.push(samples[:, :0], input_time=0.0)
        buf.push(samples, input_time=64 / SAMPLING_RATE)
        npt.assert_array_equal(buf.data(64), samples)

    def test_data_older(self) -> None:
        buf = RingBuffer()
        first = np.arange(32).reshape(1, 32)
        second = np.arange(32, 64).reshape(1, 32)
        buf.push(first, input_time=32 / SAMPLING_RATE)
        buf.push(second, input_time=64 / SAMPLING_RATE)
        npt.assert_array_equal(buf.data_older(32, 32), first)

    def test_data_time(self) -> None:
        buf = RingBuffer()
        buf.push(np.zeros((1, SAMPLING_RATE)), input_time=1.0)
        start = buf.offset - SAMPLING_RATE
        self.assertAlmostEqual(buf.data_time(start), 0.0)

    def test_grow_on_large_push(self) -> None:
        buf = RingBuffer()
        samples = np.arange(50_000).reshape(1, 50_000)
        buf.push(samples, input_time=50_000 / SAMPLING_RATE)
        npt.assert_array_equal(buf.data(50_000), samples)
