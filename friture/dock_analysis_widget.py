#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Dock analysis widget protocol and shared ingest helpers.

Dock widgets live in ``widgetdict`` and are hosted by ``Dock``. Each widget
implements this protocol so ``Dock`` can wire audio without duck typing.

Invariants for ``handle_new_data``:
- ``floatdata`` shape is ``(channels, samples)`` from ``AudioBuffer``.
- Widgets that read history use ``RingBufferFrameReader`` + ``set_buffer``.
- Widgets that only need the latest chunk may consume ``floatdata`` directly
  (levels, octave spectrum).
- ``canvasUpdate`` runs on the display timer (~25 ms); keep heavy work in
  ``handle_new_data`` or amortize across frames.

Integration tests should use ``AudioHarness`` + ``wire_dock_analysis_widget``
to mimic production wiring without starting the full app.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np
from PyQt5.QtCore import QSettings, QObject

from friture.audiobuffer import AudioBuffer


@runtime_checkable
class DockAnalysisWidget(Protocol):
    """Public surface ``Dock`` expects from an analysis widget."""

    def set_buffer(self, buffer: AudioBuffer) -> None:
        """Attach shared ring buffer; reset any read indices."""

    def handle_new_data(self, floatdata: np.ndarray) -> None:
        """Process new samples already pushed into ``AudioBuffer``."""

    def canvasUpdate(self) -> None:
        """Refresh QML-facing view models on the display timer."""

    def pause(self) -> None:
        ...

    def restart(self) -> None:
        ...

    def settings_called(self, checked: bool) -> None:
        ...

    def saveState(self, settings: QSettings) -> None:
        ...

    def restoreState(self, settings: QSettings) -> None:
        ...

    def qml_file_name(self) -> str:
        ...

    def view_model(self) -> QObject:
        ...


def is_dock_analysis_widget(widget: object) -> bool:
    return isinstance(widget, DockAnalysisWidget)


def stereo_mode_from_chunk(floatdata: np.ndarray, two_channels: bool) -> bool:
    """Return whether the UI should show a second channel strip."""
    if floatdata.shape[0] > 1 and not two_channels:
        return True
    if floatdata.shape[0] == 1 and two_channels:
        return False
    return two_channels


# Widgets not yet migrated to RingBufferFrameReader (issue #3 follow-up):
# scope, spectrogram, pitch tracker, generator, delay estimator, long levels
