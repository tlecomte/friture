# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import unittest

import numpy as np
from PyQt5.QtCore import QSettings, QObject

from friture.audiobuffer import AudioBuffer
from friture.test.helpers import AudioHarness, ensure_qapplication


class FakeDockAnalysisWidget(QObject):
    """Minimal widget used to verify the dock analysis protocol contract."""

    def __init__(self) -> None:
        super().__init__()
        self.audiobuffer: AudioBuffer | None = None
        self.chunks: list[np.ndarray] = []
        self.canvas_updates = 0
        self.paused = False

    def set_buffer(self, buffer: AudioBuffer) -> None:
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata: np.ndarray) -> None:
        self.chunks.append(floatdata.copy())

    def canvasUpdate(self) -> None:
        self.canvas_updates += 1

    def pause(self) -> None:
        self.paused = True

    def restart(self) -> None:
        self.paused = False

    def settings_called(self, checked: bool) -> None:
        del checked

    def saveState(self, settings: QSettings) -> None:
        settings.setValue("fake", True)

    def restoreState(self, settings: QSettings) -> None:
        settings.value("fake", False)

    def qml_file_name(self) -> str:
        return "Fake.qml"

    def view_model(self) -> QObject:
        return self


class DockAnalysisWidgetProtocolTest(unittest.TestCase):
    def test_fake_widget_satisfies_protocol(self) -> None:
        from friture.dock_analysis_widget import DockAnalysisWidget, is_dock_analysis_widget

        widget = FakeDockAnalysisWidget()
        self.assertTrue(is_dock_analysis_widget(widget))
        self.assertIsInstance(widget, DockAnalysisWidget)

    def test_harness_wires_buffer_to_widget_like_dock(self) -> None:
        from friture.test.helpers import wire_dock_analysis_widget

        ensure_qapplication()
        harness = AudioHarness()
        widget = FakeDockAnalysisWidget()
        wire_dock_analysis_widget(widget, harness.buffer)

        harness.push_sine(440.0, 512)
        widget.canvasUpdate()

        self.assertEqual(len(widget.chunks), 1)
        self.assertEqual(widget.chunks[0].shape[1], 512)
        self.assertEqual(widget.canvas_updates, 1)


    def test_spectrum_widget_satisfies_protocol(self) -> None:
        from friture.dock_analysis_widget import is_dock_analysis_widget
        from friture.spectrum import Spectrum_Widget

        parent = __import__("friture.test.helpers", fromlist=["make_parent_widget"]).make_parent_widget()
        widget = Spectrum_Widget(parent)
        self.assertTrue(is_dock_analysis_widget(widget))


class IngestChannelLayoutTest(unittest.TestCase):
    def test_stereo_flag_tracks_channel_count(self) -> None:
        from friture.dock_analysis_widget import stereo_mode_from_chunk

        self.assertFalse(stereo_mode_from_chunk(np.zeros((1, 8)), False))
        self.assertTrue(stereo_mode_from_chunk(np.zeros((2, 8)), False))
        self.assertFalse(stereo_mode_from_chunk(np.zeros((1, 8)), True))
