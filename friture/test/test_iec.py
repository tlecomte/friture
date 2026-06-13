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

from friture.iec import (
    dB_to_IEC,
    iec_to_dB,
    level_db_to_meter_fraction,
    meter_level_for_bar,
    normalize_unit_label,
)


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

    def test_positive_dbfs_is_clamped_to_full_scale(self) -> None:
        self.assertEqual(dB_to_IEC(10.0), 1.0)

    def test_spl_meter_maps_94_db_to_mid_scale(self) -> None:
        fraction = level_db_to_meter_fraction(94.0, "dBSPL")
        self.assertAlmostEqual(fraction, (94.0 - 40.0) / (120.0 - 40.0))
        self.assertLess(fraction, 0.9)
        self.assertGreater(fraction, 0.5)

    def test_spl_meter_clamps_to_display_range(self) -> None:
        self.assertEqual(level_db_to_meter_fraction(130.0, "dBSPL"), 1.0)
        self.assertEqual(level_db_to_meter_fraction(20.0, "dBSPL"), 0.0)

    def test_dbfs_unit_normalization(self) -> None:
        self.assertEqual(normalize_unit_label("dBFS"), "dB FS")

    def test_meter_level_for_bar_uses_raw_on_digital_unit(self) -> None:
        self.assertEqual(meter_level_for_bar(94.0, -20.0, "dB FS"), -20.0)
        self.assertEqual(meter_level_for_bar(94.0, -20.0, "dBSPL"), 94.0)
