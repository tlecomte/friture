# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

import numpy as np

from friture.level_calibration import (
    LevelCalibration,
    apply_calibration,
    calibration_offset_for_target,
    read_settings_float,
    write_settings_float,
)
from friture.test.helpers import IsolatedQSettings, ensure_qapplication


class LevelCalibrationTest(unittest.TestCase):
    def test_apply_calibration_adds_offset(self) -> None:
        self.assertAlmostEqual(apply_calibration(-20.0, 94.0), 74.0)

    def test_calibration_offset_for_target(self) -> None:
        self.assertAlmostEqual(calibration_offset_for_target(-30.0, 94.0), 124.0)

    def test_round_trip(self) -> None:
        cal = LevelCalibration(offset_db=10.0, unit_label="dBSPL")
        raw = -40.0
        self.assertAlmostEqual(apply_calibration(raw, cal.offset_db), -30.0)

    def test_apply_calibration_works_on_numpy_array(self) -> None:
        raw = np.array([-40.0, -30.0, -20.0])
        calibrated = apply_calibration(raw, 10.0)

        np.testing.assert_allclose(calibrated, [-30.0, -20.0, -10.0])


class SettingsFloatTest(unittest.TestCase):
    def setUp(self) -> None:
        ensure_qapplication()
        self.settings = IsolatedQSettings().settings

    def test_read_settings_float_reads_legacy_numpy_scalar(self) -> None:
        self.settings.setValue("offsetDb", np.float64(200.0))

        self.assertAlmostEqual(
            read_settings_float(self.settings, "offsetDb", 0.0), 200.0
        )

    def test_write_settings_float_stores_plain_python_float(self) -> None:
        write_settings_float(self.settings, "offsetDb", np.float64(15.5))

        stored = self.settings.value("offsetDb")
        self.assertIsInstance(stored, float)
        self.assertAlmostEqual(stored, 15.5)
