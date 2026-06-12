# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

import numpy as np

from friture.test.helpers import AudioHarness


class RingBufferFrameReaderTest(unittest.TestCase):
    def test_iter_frames_yields_fft_sized_slices_after_overlap(self) -> None:
        from friture.ring_buffer_frame_reader import RingBufferFrameReader

        harness = AudioHarness()
        reader = RingBufferFrameReader(frame_size=1024, overlap=0.75)
        reader.set_buffer(harness.buffer)

        harness.push_sine(440.0, 4096)
        frames = list(reader.iter_frames())

        self.assertGreaterEqual(len(frames), 1)
        self.assertEqual(frames[0].shape, (1, 1024))

    def test_set_buffer_resets_read_position(self) -> None:
        from friture.ring_buffer_frame_reader import RingBufferFrameReader

        harness = AudioHarness()
        reader = RingBufferFrameReader(frame_size=512, overlap=0.5)
        reader.set_buffer(harness.buffer)
        harness.push_sine(220.0, 2048)
        list(reader.iter_frames())

        reader.set_buffer(harness.buffer)
        frames_after_reset = list(reader.iter_frames())
        self.assertEqual(len(frames_after_reset), 0)

        harness.push_sine(220.0, 2048)
        self.assertGreaterEqual(len(list(reader.iter_frames())), 1)
