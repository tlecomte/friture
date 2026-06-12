# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

import os
import unittest

import numpy as np
import numpy.testing as npt

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QWidget

from friture.audiobackend import SAMPLING_RATE
from friture.audiobuffer import AudioBuffer
from friture.pitch_tracker import PitchTracker, PitchTrackerWidget
from friture.pitch_tracker_settings import DEFAULT_MAX_FREQ, DEFAULT_MIN_FREQ
from friture.ringbuffer import RingBuffer

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_app = QApplication.instance() or QApplication([])


def _push(buf: RingBuffer, chunk: np.ndarray, sample_offset: int) -> None:
    buf.push(chunk, sample_offset / SAMPLING_RATE)


def _sine_frame(frequency_hz: float, fft_size: int, sample_rate: int = SAMPLING_RATE) -> np.ndarray:
    t = np.linspace(0, fft_size / sample_rate, fft_size, endpoint=False)
    return np.array([np.sin(2 * np.pi * frequency_hz * t)])


class PitchTrackerTest(unittest.TestCase):
    def test_new_frames(self) -> None:
        buf = RingBuffer()
        tracker = PitchTracker(buf, fft_size=4, overlap=0.5, sample_rate=SAMPLING_RATE)
        _push(buf, np.array([np.arange(2)]), 2)
        _push(buf, np.array([np.arange(2, 5)]), 5)
        npt.assert_array_equal(
            [np.array([np.arange(4)])],
            list(tracker.new_frames()),
        )
        _push(buf, np.array([np.arange(5, 8)]), 8)
        npt.assert_array_equal(
            [np.array([np.arange(2, 6)]), np.array([np.arange(4, 8)])],
            list(tracker.new_frames()),
        )

    def test_estimate_pitch_detects_sine(self) -> None:
        buf = RingBuffer()
        tracker = PitchTracker(
            buf,
            fft_size=1024,
            overlap=0.5,
            sample_rate=SAMPLING_RATE,
            min_db=-80.0,
            conf=0.3,
        )
        pitch = tracker.estimate_pitch(_sine_frame(440.0, 1024))
        self.assertFalse(np.isnan(pitch))
        self.assertAlmostEqual(pitch, 440.0, delta=5.0)

    def test_update(self) -> None:
        buf = RingBuffer()
        fft_size = 1024
        tracker = PitchTracker(
            buf,
            fft_size=fft_size,
            overlap=0.5,
            sample_rate=SAMPLING_RATE,
            min_db=-80.0,
            conf=0.3,
        )
        _push(buf, _sine_frame(440.0, fft_size), fft_size)
        self.assertTrue(tracker.update())
        self.assertFalse(tracker.update())
        latest = tracker.get_latest_estimate()
        self.assertFalse(np.isnan(latest))
        self.assertAlmostEqual(latest, 440.0, delta=5.0)


class PitchTrackerWidgetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = QWidget()
        self.widget = PitchTrackerWidget(self.parent)
        self.settings = QSettings("friture-test", "pitch-tracker-widget")
        self.settings.clear()

    def test_changing_confidence_in_settings_updates_tracker(self) -> None:
        self.widget.settings_dialog.conf.setValue(0.33)
        self.assertAlmostEqual(self.widget.tracker.conf, 0.33)

    def test_changing_min_amplitude_in_settings_updates_tracker(self) -> None:
        self.widget.settings_dialog.min_db.setValue(-72.0)
        self.assertAlmostEqual(self.widget.tracker.min_db, -72.0)

    def test_pitch_tracker_settings_survive_save_and_restore(self) -> None:
        dialog = self.widget.settings_dialog
        dialog.conf.setValue(0.25)
        dialog.min_db.setValue(-70.0)
        dialog.min_freq.setValue(80)
        dialog.max_freq.setValue(900)
        dialog.duration.setValue(15)

        self.widget.saveState(self.settings)

        dialog.conf.setValue(0.99)
        dialog.min_db.setValue(-20.0)
        dialog.min_freq.setValue(DEFAULT_MIN_FREQ)
        dialog.max_freq.setValue(DEFAULT_MAX_FREQ)
        dialog.duration.setValue(10)

        self.widget.restoreState(self.settings)

        self.assertAlmostEqual(self.widget.tracker.conf, 0.25)
        self.assertAlmostEqual(self.widget.tracker.min_db, -70.0)
        self.assertEqual(self.widget.min_freq, 80)
        self.assertEqual(self.widget.max_freq, 900)
        self.assertEqual(self.widget.duration, 15)

    def test_settings_dialog_opens_from_widget(self) -> None:
        self.widget.settings_called(True)
        self.assertTrue(self.widget.settings_dialog.isVisible())

    def test_handle_new_data_updates_pitch_display(self) -> None:
        buffer = AudioBuffer()
        self.widget.set_buffer(buffer)
        self.widget.settings_dialog.conf.setValue(0.3)
        self.widget.settings_dialog.min_db.setValue(-80.0)

        fft_size = self.widget.tracker.fft_size
        time = np.linspace(0, fft_size / SAMPLING_RATE, fft_size, endpoint=False)
        sine = np.array([np.sin(2 * np.pi * 440.0 * time)])

        buffer.handle_new_data(sine, fft_size / SAMPLING_RATE, None)
        self.widget.handle_new_data(sine)

        view_model = self.widget.view_model()
        self.assertEqual(view_model.pitch, "440")
        self.assertEqual(view_model.note, "A4")
        self.assertFalse(np.isnan(view_model._pitch))
        self.assertAlmostEqual(view_model._pitch, 440.0, delta=5.0)
