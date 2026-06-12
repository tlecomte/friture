# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

import numpy as np

from friture.octavespectrum import OctaveSpectrum_Widget
from friture.test.helpers import AudioHarness, make_parent_widget


class OctaveSpectrumWidgetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = make_parent_widget()
        self.widget = OctaveSpectrum_Widget(self.parent)
        self.harness = AudioHarness()
        self.widget.set_buffer(self.harness.buffer)

    def test_sine_raises_octave_band_peaks(self) -> None:
        chunk = self.harness.push_sine(440.0, 12000, amplitude=0.5)
        self.widget.handle_new_data(chunk)

        self.assertGreater(float(np.max(self.widget.PlotZoneSpect.peak)), -40.0)

    def test_silence_keeps_octave_peaks_low(self) -> None:
        chunk = self.harness.push_silence(12000)
        self.widget.handle_new_data(chunk)

        self.assertLess(float(np.max(self.widget.PlotZoneSpect.peak)), -100.0)
