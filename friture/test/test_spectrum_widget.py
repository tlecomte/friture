# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

from friture.spectrum import Spectrum_Widget
from friture.test.helpers import AudioHarness, make_parent_widget


class SpectrumWidgetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = make_parent_widget()
        self.widget = Spectrum_Widget(self.parent)
        self.harness = AudioHarness()
        self.widget.set_buffer(self.harness.buffer)

    def test_sine_updates_dominant_frequency_label(self) -> None:
        fft_size = self.widget.fft_size
        chunk = self.harness.push_sine(440.0, fft_size)
        self.widget.handle_new_data(chunk)

        label = self.widget.view_model().fmaxValue
        self.assertIn("Hz", label)
        self.assertAlmostEqual(float(label.replace(" Hz", "")), 440.0, delta=5.0)

    def test_silence_does_not_crash_spectrum_update(self) -> None:
        chunk = self.harness.push_silence(self.widget.fft_size)
        self.widget.handle_new_data(chunk)

        self.assertIsNotNone(self.widget.view_model().fmaxValue)
