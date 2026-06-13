# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

from friture.db_levels_dock import DbLevelsDockWidget
from friture.freq_weighting import WEIGHTING_A
from friture.test.helpers import (
    AudioHarness,
    IsolatedQSettings,
    attach_global_calibration,
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
        attach_global_calibration(self.parent)
        self.widget = DbLevelsDockWidget(self.parent)
        self.harness = AudioHarness()
        wire_dock_analysis_widget(self.widget, self.harness.buffer)
        self.view_model = self.widget.view_model()
        self.widget.set_use_global_calibration(False)

    def _fresh_reading(self, offset_db: float, *, use_global: bool, local_offset: float = 0.0):
        parent = make_parent_widget()
        attach_global_calibration(parent)
        parent.global_calibration.set_offset_db(offset_db)
        widget = DbLevelsDockWidget(parent)
        harness = AudioHarness()
        wire_dock_analysis_widget(widget, harness.buffer)
        widget.set_use_global_calibration(use_global)
        if not use_global:
            widget.set_calibration_offset(local_offset)
        tone = harness.push_sine(440.0, 4096, amplitude=0.5)
        widget.handle_new_data(tone)
        return widget._meter.last_raw_rms_db, widget.view_model().level_data.level_rms

    def test_global_calibration_shifts_display_when_enabled(self) -> None:
        raw0, reading0 = self._fresh_reading(0.0, use_global=True)
        raw10, reading10 = self._fresh_reading(10.0, use_global=True)

        self.assertAlmostEqual(raw0, raw10, delta=1.5)
        self.assertAlmostEqual(reading10 - reading0, 10.0, delta=1.5)

    def test_local_override_shifts_display_by_10_db(self) -> None:
        _, reading0 = self._fresh_reading(0.0, use_global=False, local_offset=0.0)
        _, reading10 = self._fresh_reading(0.0, use_global=False, local_offset=10.0)

        self.assertAlmostEqual(reading10 - reading0, 10.0, delta=1.5)

    def test_calibrate_to_target_sets_local_offset_from_current_reading(self) -> None:
        from friture.level_meter import raw_rms_db_from_buffer

        tone = self.harness.push_sine(440.0, 4096, amplitude=0.5)
        raw_rms_db = raw_rms_db_from_buffer(
            self.harness.buffer,
            weighting=self.widget._meter.weighting(),
        )
        self.widget.calibrate_to_target(94.0)
        self.assertAlmostEqual(
            self.widget.local_calibration.offset_db,
            94.0 - raw_rms_db,
        )
        for _ in range(3):
            self.widget.handle_new_data(tone)
        self.assertAlmostEqual(self.view_model.level_data.level_rms, 94.0, delta=3.0)

    def test_unit_label_exposed_on_view_model(self) -> None:
        self.widget.set_unit_label("dBSPL")
        self.assertEqual(self.view_model.unit_label, "dBSPL")

    def test_weighting_suffix_exposed_on_view_model(self) -> None:
        self.widget.set_weighting(WEIGHTING_A)
        self.assertEqual(self.view_model.weighting_suffix, " (A)")

    def test_settings_round_trip(self) -> None:
        isolated = IsolatedQSettings()
        self.widget.set_use_global_calibration(False)
        self.widget.set_calibration_offset(12.5)
        self.widget.set_unit_label("dBu")
        self.widget.set_weighting(WEIGHTING_A)
        self.widget.saveState(isolated.settings)

        other_parent = make_parent_widget()
        attach_global_calibration(other_parent)
        other = DbLevelsDockWidget(other_parent)
        other.restoreState(isolated.settings)

        self.assertFalse(other.use_global_calibration)
        self.assertAlmostEqual(other.local_calibration.offset_db, 12.5)
        self.assertEqual(other.local_calibration.unit_label, "dBu")
        self.assertEqual(other._meter.weighting(), WEIGHTING_A)
