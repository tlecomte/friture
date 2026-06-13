# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

from friture.level_view_model import LevelViewModel
from friture.levels import Levels_Widget
from friture.test.helpers import AudioHarness, attach_global_calibration, make_parent_widget


class LevelsWidgetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = make_parent_widget()
        attach_global_calibration(self.parent)
        self.view_model = LevelViewModel()
        self.widget = Levels_Widget(
            self.parent, self.view_model, self.parent.global_calibration
        )
        self.harness = AudioHarness()
        self.widget.set_buffer(self.harness.buffer)

    def test_silence_stays_near_floor(self) -> None:
        chunk = self.harness.push_silence(4096)
        self.widget.handle_new_data(chunk)

        self.assertLess(self.view_model.level_data.level_rms, -90.0)

    def test_sine_is_louder_than_silence(self) -> None:
        silent = self.harness.push_silence(4096)
        self.widget.handle_new_data(silent)
        silent_rms = self.view_model.level_data.level_rms

        tone = self.harness.push_sine(440.0, 4096, amplitude=0.5)
        self.widget.handle_new_data(tone)

        self.assertGreater(self.view_model.level_data.level_rms, silent_rms + 20.0)
        self.assertGreater(self.view_model.level_data.level_max, -20.0)

    def _fresh_sidebar_reading(self, offset_db: float) -> float:
        parent = make_parent_widget()
        attach_global_calibration(parent)
        parent.global_calibration.set_offset_db(offset_db)
        view_model = LevelViewModel()
        widget = Levels_Widget(parent, view_model, parent.global_calibration)
        harness = AudioHarness()
        widget.set_buffer(harness.buffer)
        tone = harness.push_sine(440.0, 4096, amplitude=0.5)
        widget.handle_new_data(tone)
        return view_model.level_data.level_rms

    def test_global_calibration_offset_applies_to_sidebar(self) -> None:
        reading0 = self._fresh_sidebar_reading(0.0)
        reading10 = self._fresh_sidebar_reading(10.0)

        self.assertAlmostEqual(reading10 - reading0, 10.0, delta=1.5)

    def test_sidebar_meter_stays_on_iec_scale_when_unit_is_dbfs(self) -> None:
        parent = make_parent_widget()
        attach_global_calibration(parent)
        parent.global_calibration.set_offset_db(114.0)
        parent.global_calibration.set_unit_label("dB FS")
        view_model = LevelViewModel()
        widget = Levels_Widget(parent, view_model, parent.global_calibration)
        harness = AudioHarness()
        widget.set_buffer(harness.buffer)
        tone = harness.push_sine(440.0, 4096, amplitude=0.5)
        widget.handle_new_data(tone)

        self.assertGreater(view_model.level_data.level_rms, 50.0)
        self.assertLess(view_model.level_data.level_rms_iec, 0.8)

    def test_sidebar_meter_uses_spl_range_when_unit_is_dbspl(self) -> None:
        parent = make_parent_widget()
        attach_global_calibration(parent)
        parent.global_calibration.set_offset_db(100.0)
        parent.global_calibration.set_unit_label("dBSPL")
        view_model = LevelViewModel()
        widget = Levels_Widget(parent, view_model, parent.global_calibration)
        harness = AudioHarness()
        widget.set_buffer(harness.buffer)
        tone = harness.push_sine(440.0, 4096, amplitude=0.5)
        widget.handle_new_data(tone)

        self.assertGreater(view_model.level_data.level_rms, 50.0)
        self.assertLess(view_model.level_data.level_rms_iec, 0.9)
        self.assertGreater(view_model.level_data.level_rms_iec, 0.2)

    def test_stereo_input_enables_second_channel(self) -> None:
        stereo = self.harness.push(
            self.harness.push_sine(440.0, 1024).repeat(2, axis=0),
        )
        self.widget.handle_new_data(stereo)

        self.assertTrue(self.view_model.two_channels)
