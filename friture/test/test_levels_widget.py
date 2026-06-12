# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

from friture.level_view_model import LevelViewModel
from friture.levels import Levels_Widget
from friture.test.helpers import AudioHarness, make_parent_widget


class LevelsWidgetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = make_parent_widget()
        self.view_model = LevelViewModel()
        self.widget = Levels_Widget(self.parent, self.view_model)
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

    def test_stereo_input_enables_second_channel(self) -> None:
        stereo = self.harness.push(
            self.harness.push_sine(440.0, 1024).repeat(2, axis=0),
        )
        self.widget.handle_new_data(stereo)

        self.assertTrue(self.view_model.two_channels)
