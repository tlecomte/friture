#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Read fixed-size analysis frames from the shared AudioBuffer ring."""

from __future__ import annotations

from math import floor
from typing import Generator, Optional

import numpy as np

from friture.audiobuffer import AudioBuffer


class RingBufferFrameReader:
    """Track buffer offset and yield FFT-sized frames with fractional overlap.

    Invariants (same as spectrum / spectrogram docks today):
    - ``frame_size`` samples are read via ``AudioBuffer.data_indexed``.
    - Advance ``frame_size * (1 - overlap)`` samples per frame.
    - If the ring grows, unread position resets to the current write head.
    """

    def __init__(self, frame_size: int, overlap: float) -> None:
        if not 0.0 <= overlap < 1.0:
            raise ValueError("overlap must be in [0, 1)")
        self.frame_size = frame_size
        self.overlap = overlap
        self._step = int(frame_size * (1.0 - overlap))
        self._audiobuffer: Optional[AudioBuffer] = None
        self._old_index = 0

    def set_frame_size(self, frame_size: int) -> None:
        self.frame_size = frame_size
        self._step = int(frame_size * (1.0 - self.overlap))

    def set_buffer(self, buffer: AudioBuffer) -> None:
        self._audiobuffer = buffer
        self._old_index = buffer.ringbuffer.offset

    def iter_frames(self) -> Generator[np.ndarray, None, None]:
        if self._audiobuffer is None or self._step <= 0:
            return

        index = self._audiobuffer.ringbuffer.offset
        available = index - self._old_index

        if available < 0:
            available = 0
            self._old_index = index

        realizable = int(floor(available / self._step))

        for _ in range(realizable):
            frame = self._audiobuffer.data_indexed(self._old_index, self.frame_size)
            yield frame
            self._old_index += self._step
