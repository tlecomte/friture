# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Shared helpers for Friture integration tests (not a test module).

Use ``AudioHarness`` to push synthetic audio through ``AudioBuffer`` the same
way live ingest does. Use ``wire_dock_analysis_widget`` to connect a widget
with the same signals ``Dock`` uses in production.
"""

import os
import tempfile

import numpy as np
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QWidget

from friture.audiobackend import SAMPLING_RATE
from friture.audiobuffer import AudioBuffer
from friture.global_calibration import GlobalCalibrationService


def attach_global_calibration(parent: QWidget) -> GlobalCalibrationService:
    service = GlobalCalibrationService(parent)
    parent.global_calibration = service
    return service


def wire_dock_analysis_widget(widget, buffer: AudioBuffer) -> None:
    """Mirror ``Dock.widget_select`` audio wiring for tests."""
    widget.set_buffer(buffer)
    buffer.new_data_available.connect(widget.handle_new_data)


def ensure_qapplication() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def make_parent_widget() -> QWidget:
    ensure_qapplication()
    return QWidget()


class IsolatedQSettings:
    """Use a temp directory so tests never touch the user's Friture config."""

    def __init__(self) -> None:
        settings_dir = tempfile.mkdtemp(prefix="friture-qsettings-")
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, settings_dir)
        self.settings = QSettings("Friture", "Friture")
        self.settings.clear()


class AudioHarness:
    """Push synthetic audio through the same buffer path as the live app."""

    def __init__(self) -> None:
        self.buffer = AudioBuffer()

    def push(self, samples: np.ndarray, sample_offset: int | None = None) -> np.ndarray:
        if sample_offset is None:
            sample_offset = self.buffer.ringbuffer.offset + samples.shape[1]
        self.buffer.handle_new_data(
            samples,
            sample_offset / SAMPLING_RATE,
            None,
        )
        return samples

    def push_silence(self, num_samples: int) -> np.ndarray:
        return self.push(np.zeros((1, num_samples)))

    def push_sine(
        self,
        frequency_hz: float,
        num_samples: int,
        amplitude: float = 1.0,
    ) -> np.ndarray:
        time = np.linspace(0, num_samples / SAMPLING_RATE, num_samples, endpoint=False)
        samples = np.array([amplitude * np.sin(2 * np.pi * frequency_hz * time)])
        return self.push(samples)

    def latest_chunk(self) -> np.ndarray:
        return self.buffer.newdata()
