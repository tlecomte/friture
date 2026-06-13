# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import subprocess
import sys
import unittest

import numpy as np

from friture.audiobuffer import AudioBuffer
from friture.test.helpers import ensure_qapplication


class TestAudioIngestTest(unittest.TestCase):
    def test_test_ingest_feeds_audio_buffer(self) -> None:
        from friture.audio_ingest import TestAudioIngest

        ensure_qapplication()
        buffer = AudioBuffer()
        ingest = TestAudioIngest(frequency_hz=440.0)

        ingest.new_data_available.connect(buffer.handle_new_data)
        ingest.fetchAudioData()

        chunk = buffer.newdata()
        self.assertEqual(chunk.shape[0], 1)
        self.assertGreater(chunk.shape[1], 0)
        self.assertGreater(np.max(np.abs(chunk)), 0.01)


class IngestLevelsWidgetTest(unittest.TestCase):
    def test_test_ingest_drives_levels_widget(self) -> None:
        from friture.audio_ingest import TestAudioIngest
        from friture.level_view_model import LevelViewModel
        from friture.levels import Levels_Widget

        from friture.test.helpers import attach_global_calibration, make_parent_widget

        ensure_qapplication()
        parent = make_parent_widget()
        attach_global_calibration(parent)
        view_model = LevelViewModel()
        widget = Levels_Widget(parent, view_model, parent.global_calibration)
        buffer = __import__("friture.audiobuffer", fromlist=["AudioBuffer"]).AudioBuffer()
        widget.set_buffer(buffer)
        ingest = TestAudioIngest(frequency_hz=440.0, amplitude=0.8)

        ingest.new_data_available.connect(buffer.handle_new_data)
        buffer.new_data_available.connect(widget.handle_new_data)
        ingest.fetchAudioData()
        widget.canvasUpdate()

        self.assertGreater(view_model.level_data.level_rms, -20.0)


class AudioIngestFactoryTest(unittest.TestCase):
    def test_set_audio_ingest_replaces_singleton(self) -> None:
        from friture.audio_ingest import (
            TestAudioIngest,
            get_audio_ingest,
            reset_audio_ingest,
            set_audio_ingest,
        )

        reset_audio_ingest()
        try:
            ingest = TestAudioIngest(frequency_hz=220.0)
            set_audio_ingest(ingest)
            self.assertIs(get_audio_ingest(), ingest)
        finally:
            reset_audio_ingest()

    def test_importing_audiobackend_does_not_load_sounddevice(self) -> None:
        repo_root = __import__("pathlib").Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import friture.audiobackend; import sys; "
                "print('sounddevice' in sys.modules)",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "False")


class AudioIngestImportTest(unittest.TestCase):
    def test_importing_audio_ingest_does_not_load_sounddevice(self) -> None:
        repo_root = __import__("pathlib").Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import friture.audio_ingest; import sys; "
                "print('sounddevice' in sys.modules)",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "False")
