# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

from friture.level_meter import (
    calibration_quiet_message,
    calibration_raw_rms_db,
    calibration_signal_too_quiet,
    measure_raw_rms_db,
    raw_rms_db_from_buffer,
)
from friture.test.helpers import AudioHarness, ensure_qapplication
from friture.level_calibration import LevelCalibration
from friture.level_meter import LevelMeterProcessor
from friture.level_view_model import LevelViewModel


class RawRmsMeasurementTest(unittest.TestCase):
    def test_measure_raw_rms_db_from_sine(self) -> None:
        harness = AudioHarness()
        chunk = harness.push_sine(440.0, 4096, amplitude=0.5)

        raw = measure_raw_rms_db(chunk[0])

        self.assertGreater(raw, -20.0)
        self.assertLess(raw, 0.0)

    def test_raw_rms_db_from_buffer_uses_recent_audio(self) -> None:
        harness = AudioHarness()
        harness.push_sine(440.0, 4096, amplitude=0.5)

        raw = raw_rms_db_from_buffer(harness.buffer)

        self.assertGreater(raw, -20.0)

    def test_empty_buffer_returns_floor(self) -> None:
        harness = AudioHarness()

        self.assertLessEqual(raw_rms_db_from_buffer(harness.buffer), -100.0)

    def test_calibration_raw_rms_db_uses_live_meter_when_louder(self) -> None:
        ensure_qapplication()
        harness = AudioHarness()
        chunk = harness.push_sine(1000.0, 4096, amplitude=0.5)
        meter = LevelMeterProcessor()
        view_model = LevelViewModel(None)
        calibration = LevelCalibration()
        for start in range(0, 4096, 1024):
            meter.handle_new_data(chunk[:, start : start + 1024], view_model, calibration)
        harness.push_silence(4096)

        from_buffer = raw_rms_db_from_buffer(harness.buffer)
        combined = calibration_raw_rms_db(harness.buffer, meter=meter)

        self.assertTrue(calibration_signal_too_quiet(from_buffer))
        self.assertFalse(calibration_signal_too_quiet(combined))
        self.assertAlmostEqual(combined, meter.last_raw_rms_db)

    def test_calibration_quiet_message_explains_offset_inflated_readings(self) -> None:
        message = calibration_quiet_message(
            -114.4,
            offset_db=200.0,
            unit_label="dBSPL",
        )

        self.assertIn("-114.4 dBFS", message)
        self.assertIn("200.0 dB", message)
        self.assertIn("offset", message.lower())
