# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

from friture.longlevels import LongLevelWidget
from friture.test.helpers import IsolatedQSettings, make_parent_widget


class LongLevelsCalibrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = make_parent_widget()
        self.widget = LongLevelWidget(self.parent)

    def test_unit_label_updates_axis_name(self) -> None:
        self.widget.set_unit_label("dBSPL")

        self.assertEqual(
            self.widget.view_model().vertical_axis.name,
            "Level (dBSPL RMS)",
        )

    def test_calibrate_to_target_sets_offset_from_last_raw_reading(self) -> None:
        self.widget.last_raw_rms_db = -40.0

        self.widget.calibrate_to_target(-30.0)

        self.assertAlmostEqual(self.widget.calibration.offset_db, 10.0)

    def test_settings_round_trip(self) -> None:
        isolated = IsolatedQSettings()
        self.widget.set_calibration_offset(8.0)
        self.widget.set_unit_label("dBu")
        self.widget.set_reference_note("94 dB cal")
        self.widget.saveState(isolated.settings)

        other = LongLevelWidget(self.parent)
        other.restoreState(isolated.settings)

        self.assertAlmostEqual(other.calibration.offset_db, 8.0)
        self.assertEqual(other.calibration.unit_label, "dBu")
        self.assertEqual(other.calibration.reference_note, "94 dB cal")
