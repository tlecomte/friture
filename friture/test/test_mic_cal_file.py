# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import os
import unittest

import numpy as np

from friture.mic_cal_file import MicCalFile, MicCalFileError, load_mic_cal_file


FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class MicCalFileParserTest(unittest.TestCase):
    def test_loads_factory_format_with_sensitivity_header(self) -> None:
        cal = load_mic_cal_file(os.path.join(FIXTURES, "mic_cal_factory.txt"))

        self.assertAlmostEqual(cal.sensitivity_db, -38.6)
        self.assertAlmostEqual(cal.reference_freq_hz, 1000.0)
        self.assertGreaterEqual(len(cal.frequencies_hz), 3)
        idx_1k = np.argmin(np.abs(cal.frequencies_hz - 1000.0))
        self.assertAlmostEqual(cal.corrections_db[idx_1k], 0.0, delta=0.05)
        idx_10k = np.argmin(np.abs(cal.frequencies_hz - 10000.0))
        self.assertAlmostEqual(cal.corrections_db[idx_10k], 2.2, delta=0.05)

    def test_loads_rew_format_with_dbfs_sensitivity(self) -> None:
        cal = load_mic_cal_file(os.path.join(FIXTURES, "mic_cal_rew.cal"))

        self.assertAlmostEqual(cal.sensitivity_db, -12.34)
        self.assertAlmostEqual(cal.interpolate_db(np.array([1000.0]))[0], 0.0, delta=0.05)
        self.assertAlmostEqual(cal.interpolate_db(np.array([10000.0]))[0], 1.5, delta=0.05)

    def test_interpolate_uses_log_spacing(self) -> None:
        cal = load_mic_cal_file(os.path.join(FIXTURES, "mic_cal_factory.txt"))
        mid = cal.interpolate_db(np.array([632.0]))[0]

        self.assertGreater(mid, 0.0)
        self.assertLess(mid, 0.5)

    def test_rejects_file_without_frequency_points(self) -> None:
        with self.assertRaises(MicCalFileError):
            MicCalFile.parse_text("*1000Hz -38.6\n")

    def test_summary_includes_serial_from_filename(self) -> None:
        cal = load_mic_cal_file(os.path.join(FIXTURES, "mic_cal_factory.txt"))

        self.assertIn("-38.6", cal.summary())
        self.assertIn("1000", cal.summary())
