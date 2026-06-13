# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

from friture.longlevels import LongLevelWidget
from friture.level_meter import raw_rms_db_from_buffer
from friture.test.helpers import (
    AudioHarness,
    IsolatedQSettings,
    attach_global_calibration,
    make_parent_widget,
)


class LongLevelsCalibrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = make_parent_widget()
        attach_global_calibration(self.parent)
        self.widget = LongLevelWidget(self.parent)
        self.widget.set_use_global_calibration(False)

    def test_unit_label_updates_axis_name(self) -> None:
        self.widget.set_unit_label("dBSPL")

        self.assertEqual(
            self.widget.view_model().vertical_axis.name,
            "Level (dBSPL RMS)",
        )

    def test_global_unit_label_updates_axis_when_enabled(self) -> None:
        self.widget.set_use_global_calibration(True)
        self.parent.global_calibration.set_unit_label("dBSPL")

        self.assertEqual(
            self.widget.view_model().vertical_axis.name,
            "Level (dBSPL RMS)",
        )

    def test_calibrate_to_target_sets_offset_from_current_buffer(self) -> None:
        harness = AudioHarness()
        self.widget.set_buffer(harness.buffer)
        harness.push_sine(440.0, 4096, amplitude=0.5)
        raw_rms_db = raw_rms_db_from_buffer(harness.buffer)

        self.widget.calibrate_local_to_target(raw_rms_db, raw_rms_db + 10.0)

        self.assertAlmostEqual(self.widget.local_calibration.offset_db, 10.0)

    def test_settings_round_trip(self) -> None:
        isolated = IsolatedQSettings()
        self.widget.set_use_global_calibration(False)
        self.widget.set_calibration_offset(8.0)
        self.widget.set_unit_label("dBu")
        self.widget.set_reference_note("94 dB cal")
        self.widget.saveState(isolated.settings)

        other = LongLevelWidget(self.parent)
        other.restoreState(isolated.settings)

        self.assertFalse(other.use_global_calibration)
        self.assertAlmostEqual(other.local_calibration.offset_db, 8.0)
        self.assertEqual(other.local_calibration.unit_label, "dBu")
        self.assertEqual(other.local_calibration.reference_note, "94 dB cal")
