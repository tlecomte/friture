#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Audio ingest seam: capture adapters push frames into the app."""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
from numpy import ndarray
from PyQt5 import QtCore

SAMPLING_RATE = 48000
FRAMES_PER_BUFFER = 512

__ingest_instance: Optional[QtCore.QObject] = None


class TestAudioIngest(QtCore.QObject):
    """Synthetic capture for tests — emits sine frames on fetchAudioData."""

    underflow = QtCore.pyqtSignal()
    new_data_available = QtCore.pyqtSignal(ndarray, float, bool)

    def __init__(
        self,
        frequency_hz: float = 440.0,
        amplitude: float = 0.5,
        frames_per_buffer: int = FRAMES_PER_BUFFER,
    ) -> None:
        super().__init__()
        self.frequency_hz = frequency_hz
        self.amplitude = amplitude
        self.frames_per_buffer = frames_per_buffer
        self._sample_index = 0
        self.chunk_number = 0
        self.xruns = 0
        self.duo_input = False

    def fetchAudioData(self) -> None:
        time = (
            np.arange(self.frames_per_buffer, dtype=np.float64) + self._sample_index
        ) / SAMPLING_RATE
        samples = self.amplitude * np.sin(2 * np.pi * self.frequency_hz * time)
        floatdata = samples.reshape(1, -1)
        stream_time = self._sample_index / SAMPLING_RATE
        self._sample_index += self.frames_per_buffer
        self.chunk_number += 1
        self.new_data_available.emit(floatdata, stream_time, False)

    def close(self) -> None:
        pass

    def pause(self) -> None:
        pass

    def restart(self) -> None:
        self._sample_index = 0

    def get_stream_time(self) -> float:
        return self._sample_index / SAMPLING_RATE

    def get_readable_devices_list(self) -> list[str]:
        return ["Test Input (1 channels) (test)"]

    def get_readable_current_channels(self) -> list[str]:
        return ["0"]

    def get_readable_current_device(self) -> int:
        return 0

    def get_current_first_channel(self) -> int:
        return 0

    def get_current_second_channel(self) -> int:
        return 0

    def select_input_device(self, index: int) -> tuple[bool, int]:
        return True, index

    def select_first_channel(self, index: int) -> tuple[bool, int]:
        return True, index

    def select_second_channel(self, index: int) -> tuple[bool, int]:
        return True, index

    def set_single_input(self) -> None:
        self.duo_input = False

    def set_duo_input(self) -> None:
        self.duo_input = True


def create_test_ingest(**kwargs) -> TestAudioIngest:
    return TestAudioIngest(**kwargs)


def create_portaudio_ingest() -> QtCore.QObject:
    from friture.portaudio_ingest import PortAudioIngest

    return PortAudioIngest()


def get_audio_ingest() -> QtCore.QObject:
    global __ingest_instance
    if __ingest_instance is None:
        __ingest_instance = create_portaudio_ingest()
    return __ingest_instance


def set_audio_ingest(ingest: Optional[QtCore.QObject]) -> None:
    global __ingest_instance
    __ingest_instance = ingest


def reset_audio_ingest() -> None:
    global __ingest_instance
    if __ingest_instance is not None:
        close = getattr(__ingest_instance, "close", None)
        if close is not None:
            close()
    __ingest_instance = None


def get_audio_ingest_logger() -> logging.Logger:
    return logging.getLogger(__name__)
