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

from friture.iec import dB_to_IEC, iec_to_dB


class IECTest(unittest.TestCase):
    def test_below_meter_range(self) -> None:
        self.assertEqual(dB_to_IEC(-80.0), 0.0)

    def test_quiet_segment(self) -> None:
        self.assertAlmostEqual(dB_to_IEC(-65.0), 0.0125)

    def test_mid_level(self) -> None:
        self.assertAlmostEqual(dB_to_IEC(-39.0), 0.165)

    def test_loud_segment(self) -> None:
        self.assertAlmostEqual(dB_to_IEC(-10.0), 0.75)

    def test_segment_boundaries_are_continuous(self) -> None:
        boundaries = [-70.0, -60.0, -50.0, -40.0, -30.0, -20.0]
        for dB in boundaries:
            self.assertAlmostEqual(dB_to_IEC(dB - 1e-9), dB_to_IEC(dB))

    def test_iec_to_dB_inverts_dB_to_IEC(self) -> None:
        for dB in [-65.0, -39.0, -10.0, 0.0]:
            self.assertAlmostEqual(iec_to_dB(dB_to_IEC(dB)), dB, places=5)
