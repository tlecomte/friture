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

DEFAULT_HISTORY_LENGTH_S = 5

class PlayState(Enum):
    STOPPED = 0
    PLAYING = 1
    STOPPING = 2

class Player(QObject):
    stopping = pyqtSignal()
    stopped = pyqtSignal()

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self.history_sec = DEFAULT_HISTORY_LENGTH_S
        self.history_samples = self.history_sec * SAMPLING_RATE
        self.buffer = RingBuffer()
        self.buffer.grow_if_needed(self.history_samples)
        self.recorded_len = 0
        self.stopping.connect(self.on_stopping)

        self.device: Optional[Dict[str, Any]] = None
        self.stream: Optional[OutputStream] = None
        self.out_channels: int = 0
        self.play_offset = 0
        self.state = PlayState.STOPPED

    def handle_new_data(self, data: np.ndarray) -> None:
        # this will zero out history if channel count changes, not ideal but
        # probably doesn't matter
        self.buffer.push(data)
        self.recorded_len = min(
            self.recorded_len + data.shape[1], self.history_samples)

    def play(self) -> None:
        log.info(f"Playing back {self.recorded_len} samples")
        if self.stream is None:
            for device in AudioBackend().output_devices:
                log.info(f"Opening stream for {device['name']}")
                try:
                    self.stream = AudioBackend().open_output_stream(
                        device, self.output_callback)
                    self.stream.start()
                    self.device = device
                except Exception:
                    log.exception("Failed to open stream")
                else:
                    break
        self.out_channels = AudioBackend().get_device_outputchannels_count(self.device)
        self.play_offset = self.buffer.offset - self.recorded_len
        self.state = PlayState.PLAYING

    def output_callback(
        self,
        out_data: np.ndarray,
        samples: int,
        time_info: float,
        status: str
    ) -> None:
        if status:
            log.info(status)

        res = np.zeros((self.out_channels, samples))
        available = self.buffer.offset - self.play_offset
        to_copy = min(available, samples)
        self.play_offset += to_copy

        if available < samples and self.state == PlayState.PLAYING:
            log.info("Playback stopping")
            self.state = PlayState.STOPPING
            self.stopping.emit()

        in_channels = self.buffer.buffer.shape[0]
        if in_channels == 1:
            # Mono recording, duplicate to all output channels:
            for i in range(self.out_channels):
                res[i,0:to_copy] = self.buffer.data_indexed(
                    self.play_offset, samples)[0,0:to_copy]
        else:
            # Stereo+ recording, leave higher out channels zero if present
            copy_channels = min(self.out_channels, self.buffer.buffer.shape[0])
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