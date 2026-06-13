# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

import numpy as np

from friture.global_calibration import GlobalCalibrationService
from friture.level_calibration import LevelCalibration, resolve_calibration
from friture.test.helpers import IsolatedQSettings, ensure_qapplication, make_parent_widget


class ResolveCalibrationTest(unittest.TestCase):
    def test_uses_global_when_enabled(self) -> None:
        global_cal = LevelCalibration(offset_db=12.0, unit_label="dBSPL")
        local_cal = LevelCalibration(offset_db=3.0, unit_label="dBu")

        effective = resolve_calibration(global_cal, local_cal, use_global=True)

        self.assertAlmostEqual(effective.offset_db, 12.0)
        self.assertEqual(effective.unit_label, "dBSPL")

    def test_uses_local_when_override_enabled(self) -> None:
        global_cal = LevelCalibration(offset_db=12.0, unit_label="dBSPL")
        local_cal = LevelCalibration(offset_db=3.0, unit_label="dBu")

        effective = resolve_calibration(global_cal, local_cal, use_global=False)

        self.assertAlmostEqual(effective.offset_db, 3.0)
        self.assertEqual(effective.unit_label, "dBu")


class GlobalCalibrationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        ensure_qapplication()
        self.parent = make_parent_widget()
        self.service = GlobalCalibrationService(self.parent)

    def test_calibrate_to_target_sets_offset(self) -> None:
        self.service.calibrate_to_target(-40.0, 94.0)

        self.assertAlmostEqual(self.service.calibration.offset_db, 134.0)

    def test_settings_round_trip(self) -> None:
        isolated = IsolatedQSettings()
        self.service.set_offset_db(15.5)
        self.service.set_unit_label("dBu")
        self.service.set_reference_note("pistonphone")
        self.service.saveState(isolated.settings)

        other_parent = make_parent_widget()
        other = GlobalCalibrationService(other_parent)
        other.restoreState(isolated.settings)
        self.other_parent = other_parent

        self.assertAlmostEqual(other.calibration.offset_db, 15.5)
        self.assertEqual(other.calibration.unit_label, "dBu")
        self.assertEqual(other.calibration.reference_note, "pistonphone")

    def test_recovers_legacy_numpy_offset_in_settings(self) -> None:
        isolated = IsolatedQSettings()
        isolated.settings.setValue("offsetDb", np.float64(200.0))
        isolated.settings.setValue("unitLabel", "dB FS")

        other_parent = make_parent_widget()
        other = GlobalCalibrationService(other_parent)
        other.restoreState(isolated.settings)
        self.other_parent = other_parent

        self.assertAlmostEqual(other.calibration.offset_db, 200.0)
        stored = isolated.settings.value("offsetDb")
        self.assertIsInstance(stored, float)
        self.assertAlmostEqual(stored, 200.0)
