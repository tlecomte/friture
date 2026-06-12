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

import os
import unittest

from PyQt5.QtWidgets import QApplication

from friture.ballistic_peak import PEAK_FALLOFF, BallisticPeak

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_app = QApplication.instance() or QApplication([])


class BallisticPeakTest(unittest.TestCase):
    def test_peak_follows_rising_input(self) -> None:
        peak = BallisticPeak()

        peak.peak_iec = 0.2
        peak.peak_iec = 0.5

        self.assertAlmostEqual(peak.peak_iec, 0.5)

    def test_peak_holds_before_decay(self) -> None:
        peak = BallisticPeak()
        peak.peak_iec = 0.8

        for _ in range(PEAK_FALLOFF):
            peak.peak_iec = 0.1
            self.assertAlmostEqual(peak.peak_iec, 0.8)
