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

from friture.iec import dB_to_IEC
from friture.level_data import LevelData

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_app = QApplication.instance() or QApplication([])


class LevelDataTest(unittest.TestCase):
    def test_level_rms_iec_reflects_db_reading(self) -> None:
        level = LevelData()
        level.level_rms = -30.0

        self.assertAlmostEqual(level.level_rms_iec, dB_to_IEC(-30.0))

    def test_level_max_iec_reflects_db_reading(self) -> None:
        level = LevelData()
        level.level_max = -10.0

        self.assertAlmostEqual(level.level_max_iec, dB_to_IEC(-10.0))
