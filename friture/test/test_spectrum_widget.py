# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

from friture.spectrum import Spectrum_Widget
from friture.test.helpers import AudioHarness, attach_global_calibration, make_parent_widget


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

    def test_mic_cal_file_shifts_spectrum_at_high_frequency(self) -> None:
        import os

        parent = make_parent_widget()
        attach_global_calibration(parent)
        cal_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "mic_cal_factory.txt"
        )
        parent.global_calibration.set_mic_cal_file(cal_path)

        baseline_widget = Spectrum_Widget(parent)
        baseline_harness = AudioHarness()
        baseline_widget.set_buffer(baseline_harness.buffer)
        parent.global_calibration.clear_mic_cal_file()

        fft_size = baseline_widget.fft_size
        chunk = baseline_harness.push_sine(10000.0, fft_size, amplitude=0.5)
        baseline_widget.handle_new_data(chunk)
        baseline_peak = float(baseline_widget.PlotZoneSpect.peak.max())

        parent.global_calibration.set_mic_cal_file(cal_path)
        calibrated_widget = Spectrum_Widget(parent)
        calibrated_harness = AudioHarness()
        calibrated_widget.set_buffer(calibrated_harness.buffer)
        chunk = calibrated_harness.push_sine(10000.0, fft_size, amplitude=0.5)
        calibrated_widget.handle_new_data(chunk)
        calibrated_peak = float(calibrated_widget.PlotZoneSpect.peak.max())

        self.assertAlmostEqual(calibrated_peak - baseline_peak, -2.2, delta=1.0)

    def test_scalar_offset_shifts_axis_not_trace_saturation(self) -> None:
        parent = make_parent_widget()
        attach_global_calibration(parent)
        parent.global_calibration.set_offset_db(114.0)

        widget = Spectrum_Widget(parent)
        harness = AudioHarness()
        widget.set_buffer(harness.buffer)
        widget.setmin(-100)
        widget.setmax(-20)

        chunk = harness.push_sine(440.0, widget.fft_size, amplitude=0.5)
        widget.handle_new_data(chunk)

        self.assertAlmostEqual(widget.spec_min, 14.0, delta=1.0)
        self.assertAlmostEqual(widget.spec_max, 94.0, delta=1.0)
        peak = float(widget.PlotZoneSpect.peak.max())
        self.assertGreater(peak, widget.spec_min + 5.0)
        self.assertLess(peak, widget.spec_max - 5.0)

