# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

from friture.db_levels_dock import DbLevelsDockWidget
from friture.freq_weighting import WEIGHTING_A
from friture.test.helpers import (
    AudioHarness,
    IsolatedQSettings,
    make_parent_widget,
    wire_dock_analysis_widget,
)
from friture.widgetdict import DB_LEVELS_WIDGET_ID, getWidgetById, widgetIds


class WidgetDictDbLevelsTest(unittest.TestCase):
    def test_db_levels_registered_as_id_9(self) -> None:
        self.assertIn(DB_LEVELS_WIDGET_ID, widgetIds())
        descriptor = getWidgetById(DB_LEVELS_WIDGET_ID)
        self.assertEqual(descriptor["Name"], "dB levels")
        self.assertIs(descriptor["Class"], DbLevelsDockWidget)


class DbLevelsDockWidgetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = make_parent_widget()
        self.widget = DbLevelsDockWidget(self.parent)
        self.harness = AudioHarness()
        wire_dock_analysis_widget(self.widget, self.harness.buffer)
        self.view_model = self.widget.view_model()

    def test_calibration_offset_shifts_display_by_10_db(self) -> None:
        tone = self.harness.push_sine(440.0, 4096, amplitude=0.5)

        baseline = DbLevelsDockWidget(make_parent_widget())
        wire_dock_analysis_widget(baseline, self.harness.buffer)
        baseline.set_calibration_offset(0.0)
        baseline.handle_new_data(tone)
        base_reading = baseline.view_model().level_data.level_rms

        calibrated = DbLevelsDockWidget(make_parent_widget())
        wire_dock_analysis_widget(calibrated, self.harness.buffer)
        calibrated.set_calibration_offset(10.0)
        calibrated.handle_new_data(tone)

        self.assertAlmostEqual(
            calibrated.view_model().level_data.level_rms,
            base_reading + 10.0,
        )

    def test_calibrate_to_target_sets_offset_from_current_reading(self) -> None:
        tone = self.harness.push_sine(440.0, 4096, amplitude=0.5)
        self.widget.handle_new_data(tone)

        self.widget.calibrate_to_target(94.0)
        self.widget.handle_new_data(tone)

        self.assertAlmostEqual(self.view_model.level_data.level_rms, 94.0, delta=2.0)

    def test_unit_label_exposed_on_view_model(self) -> None:
        self.widget.set_unit_label("dBSPL")
        self.assertEqual(self.view_model.unit_label, "dBSPL")

    def test_weighting_suffix_exposed_on_view_model(self) -> None:
        self.widget.set_weighting(WEIGHTING_A)
        self.assertEqual(self.view_model.weighting_suffix, " (A)")

    def test_settings_round_trip(self) -> None:
        isolated = IsolatedQSettings()
        self.widget.set_calibration_offset(12.5)
        self.widget.set_unit_label("dBu")
        self.widget.set_weighting(WEIGHTING_A)
        self.widget.saveState(isolated.settings)

        other = DbLevelsDockWidget(make_parent_widget())
        other.restoreState(isolated.settings)

        self.assertAlmostEqual(other.calibration.offset_db, 12.5)
        self.assertEqual(other.calibration.unit_label, "dBu")
        self.assertEqual(other._meter.weighting(), WEIGHTING_A)
