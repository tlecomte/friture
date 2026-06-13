# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import os
import unittest

import numpy as np

from friture.global_frequency_calibration import frequency_adjustment_db
from friture.mic_cal_file import load_mic_cal_file
from friture.test.helpers import IsolatedQSettings, ensure_qapplication, make_parent_widget


FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class FrequencyAdjustmentTest(unittest.TestCase):
    def test_scalar_offset_only_without_mic_cal(self) -> None:
        adjustment = frequency_adjustment_db(np.array([440.0, 1000.0]), offset_db=10.0)

        np.testing.assert_allclose(adjustment, [10.0, 10.0])

    def test_mic_cal_subtracts_frequency_correction(self) -> None:
        mic_cal = load_mic_cal_file(os.path.join(FIXTURES, "mic_cal_factory.txt"))
        adjustment = frequency_adjustment_db(
            np.array([1000.0, 10000.0]),
            offset_db=0.0,
            mic_cal=mic_cal,
        )

        self.assertAlmostEqual(adjustment[0], 0.0, places=1)
        self.assertAlmostEqual(adjustment[1], -2.2, places=1)

    def test_calibrated_spec_range_shifts_by_scalar_offset(self) -> None:
        from friture.global_frequency_calibration import calibrated_spec_range
        from friture.test.helpers import attach_global_calibration

        ensure_qapplication()
        parent = make_parent_widget()
        service = attach_global_calibration(parent)
        service.set_offset_db(114.0)

        spec_min, spec_max = calibrated_spec_range(-100.0, -20.0, parent)

        self.assertAlmostEqual(spec_min, 14.0)
        self.assertAlmostEqual(spec_max, 94.0)


class GlobalCalibrationMicCalTest(unittest.TestCase):
    def setUp(self) -> None:
        ensure_qapplication()
        self.parent = make_parent_widget()
        from friture.global_calibration import GlobalCalibrationService

        self.service = GlobalCalibrationService(self.parent)

    def test_load_mic_cal_file_persists_in_settings(self) -> None:
        path = os.path.join(FIXTURES, "mic_cal_factory.txt")
        self.service.set_mic_cal_file(path)

        isolated = IsolatedQSettings()
        self.service.saveState(isolated.settings)

        other_parent = make_parent_widget()
        from friture.global_calibration import GlobalCalibrationService

        other = GlobalCalibrationService(other_parent)
        other.restoreState(isolated.settings)
        self.other_parent = other_parent

        self.assertEqual(other.mic_cal_file_path, os.path.abspath(path))
        self.assertIsNotNone(other.mic_cal)
        assert other.mic_cal is not None
        self.assertAlmostEqual(other.mic_cal.sensitivity_db, -38.6)
        self.assertAlmostEqual(
            other.frequency_adjustment_db(np.array([10000.0]))[0],
            -2.2,
            places=1,
        )
