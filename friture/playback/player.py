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

from enum import Enum
import logging
from typing import Any, Dict, Optional

from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np
from sounddevice import OutputStream

from friture.audiobackend import AudioBackend, SAMPLING_RATE
from friture.ringbuffer import RingBuffer

log = logging.getLogger(__name__)

DEFAULT_HISTORY_LENGTH_S = 30

class PlayState(Enum):
    STOPPED = 0
    PLAYING = 1
    STOPPING = 2

class Player(QObject):
    stopping = pyqtSignal()
    stopped = pyqtSignal()
    recorded_length_changed = pyqtSignal(float)
    playback_time_changed = pyqtSignal(float)

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self.history_sec = DEFAULT_HISTORY_LENGTH_S
        self.history_samples = self.history_sec * SAMPLING_RATE
        self.buffer = RingBuffer()
        self.buffer.grow_if_needed(self.history_samples)
        self.recorded_len = 0
        self.stopping.connect(self.on_stopping)

        # If zero, play starts at beginning of buffer. Otherwise, this
        # is a negative offset in seconds from the end of the buffer.
        self.play_start_time = 0.0

        self.device: Optional[Dict[str, Any]] = None
        self.stream: Optional[OutputStream] = None
        self.play_offset = 0
        self.state = PlayState.STOPPED

    def set_history_seconds(self, new_len: int) -> None:
        if new_len <= 0:
            raise ValueError("History must have positive length")

        self.history_sec = new_len
        self.history_samples = self.history_sec * SAMPLING_RATE
        self.buffer.grow_if_needed(self.history_samples)

        # Handle the case where the current play position is truncated out
        # (will result in a skip in playback)
        if self.state == PlayState.PLAYING:
            if self.play_offset < (self.buffer.offset - self.history_samples):
                self.play_offset = self.buffer.offset - self.history_samples
                self.playback_time_changed.emit(
                    (self.play_offset - self.buffer.offset) / SAMPLING_RATE)

        # Handle the case where the selected start time is truncated
        if self.play_start_time < -self.history_sec:
            self.play_start_time = -self.history_sec
            # Start time == playback time only when not playing
            if self.state != PlayState.PLAYING:
                self.playback_time_changed.emit(-self.history_sec)

        # Note that this sets the valid range for the slider, and the current
        # position will have been adjusted to fit, above.
        if self.history_samples < self.recorded_len:
            self.recorded_len = self.history_samples
            self.recorded_length_changed.emit(self.recorded_len / SAMPLING_RATE)

    def handle_new_data(self, data: np.ndarray) -> None:
        # this will zero out history if channel count changes, not ideal but
        # probably doesn't matter
        self.buffer.push(data)
        new_len = min(
            self.recorded_len + data.shape[1], self.history_samples)
        if new_len != self.recorded_len:
            self.recorded_len = new_len
            self.recorded_length_changed.emit(self.recorded_len_sec)

    @property
    def recorded_len_sec(self) -> float:
        return self.recorded_len / SAMPLING_RATE

    def play(self) -> None:
        if self.state != PlayState.STOPPED:
            log.info("Already playing!")
            return
        self.state = PlayState.PLAYING

        log.info(f"Playing back {self.recorded_len} samples")
        if self.stream is None:
            for device in AudioBackend().output_devices:
                log.info(f"Opening stream for {device['name']}")
                try:
                    self.device = device
                    self.stream = AudioBackend().open_output_stream(
                        device, self.output_callback)
                    self.stream.start()
                except Exception:
                    log.exception("Failed to open stream")
                else:
                    break

        if self.play_start_time == 0.0:
            self.play_offset = self.buffer.offset - self.recorded_len
        else:
            start_offset = max(
                -self.recorded_len,
                int(self.play_start_time * SAMPLING_RATE)
            )
            self.play_offset = self.buffer.offset + start_offset

    def stop(self) -> None:
        if self.state == PlayState.PLAYING:
            self.on_stopping()

    def is_stopped(self) -> bool:
        return self.state == PlayState.STOPPED

    def output_callback(
        self,
        out_data: np.ndarray,
        samples: int,
        time_info: float,
        status: str
    ) -> None:
        if status:
            log.info(status)

        out_channels = AudioBackend().get_device_outputchannels_count(self.device)
        res = np.zeros((out_channels, samples))
        available = self.buffer.offset - self.play_offset
        to_copy = min(available, samples)
        self.play_offset += to_copy
        self.playback_time_changed.emit(
            (self.play_offset - self.buffer.offset) / SAMPLING_RATE)

        if available < samples and self.state == PlayState.PLAYING:
            log.info("Reached end of playback")
            self.state = PlayState.STOPPING
            self.stopping.emit()

        in_channels = self.buffer.buffer.shape[0]
        if in_channels == 1:
            # Mono recording, duplicate to all output channels:
            for i in range(out_channels):
                res[i,0:to_copy] = self.buffer.data_indexed(
                    self.play_offset, samples)[0,0:to_copy]
        else:
            # Stereo+ recording, leave higher out channels zero if present
            copy_channels = min(out_channels, self.buffer.buffer.shape[0])
            res[0:copy_channels,0:to_copy] = self.buffer.data_indexed(
                self.play_offset, samples)[0:copy_channels,0:to_copy]

        # Buffer is float in [-1, 1], output is int16, need to convert scales
        int16info = np.iinfo(np.int16)
        scale = min(abs(int16info.min), int16info.max)
        res = scale * np.clip(res, -1.0, 1.0)
        res = res.astype(np.int16)

        # Buffer is channel-major, output is time-major
        res = res.transpose()

        out_data[:] = res


    def on_stopping(self) -> None:
        assert self.stream is not None
        self.stream.stop()
        self.stream = None
        self.state = PlayState.STOPPED
        self.stopped.emit()
