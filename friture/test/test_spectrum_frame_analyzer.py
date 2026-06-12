# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

import numpy as np

from friture.audiobackend import SAMPLING_RATE
from friture.spectrum_settings import DEFAULT_FFT_SIZE


class SpectrumFrameAnalyzerTest(unittest.TestCase):
    def test_sine_frame_peak_near_440_hz_without_qt(self) -> None:
        from friture.spectrum_frame_analyzer import SpectrumFrameAnalyzer

        fft_size = 2 ** DEFAULT_FFT_SIZE * 32
        analyzer = SpectrumFrameAnalyzer(fft_size=fft_size)

        time = np.linspace(0, fft_size / SAMPLING_RATE, fft_size, endpoint=False)
        frame = np.array([0.5 * np.sin(2 * np.pi * 440.0 * time)])

        result = analyzer.process_frames([frame])

        self.assertIsNotNone(result)
        assert result is not None
        self.assertAlmostEqual(result.fmax_hz, 440.0, delta=5.0)

    def test_smoothing_state_stays_inside_analyzer(self) -> None:
        from friture.spectrum_frame_analyzer import SpectrumFrameAnalyzer

        fft_size = 2048
        analyzer = SpectrumFrameAnalyzer(fft_size=fft_size)
        frame = np.zeros((1, fft_size))

        analyzer.process_frames([frame])
        self.assertTrue(hasattr(analyzer, "_dispbuffers1"))
        self.assertFalse(hasattr(analyzer, "dispbuffers1"))
