# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

from friture.level_calibration import (
    LevelCalibration,
    apply_calibration,
    calibration_offset_for_target,
)


class LevelCalibrationTest(unittest.TestCase):
    def test_apply_calibration_adds_offset(self) -> None:
        self.assertAlmostEqual(apply_calibration(-20.0, 94.0), 74.0)

    def test_calibration_offset_for_target(self) -> None:
        self.assertAlmostEqual(calibration_offset_for_target(-30.0, 94.0), 124.0)

    def test_round_trip(self) -> None:
        cal = LevelCalibration(offset_db=10.0, unit_label="dBSPL")
        raw = -40.0
        self.assertAlmostEqual(apply_calibration(raw, cal.offset_db), -30.0)
