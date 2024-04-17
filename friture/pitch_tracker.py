#!/usr/bin/env python
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

from collections.abc import Generator
import logging
import math as m
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtProperty # type: ignore
from PyQt5.QtCore import QObject, QSettings, Qt
from PyQt5.QtQuick import QQuickWindow
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtQml import QQmlComponent, QQmlEngine
from typing import Any, Optional

from friture.audiobackend import SAMPLING_RATE
from friture.audiobuffer import AudioBuffer
from friture.audioproc import audioproc
from friture.curve import Curve
from friture.pitch_tracker_settings import (
    DEFAULT_MIN_FREQ,
    DEFAULT_MAX_FREQ,
    DEFAULT_DURATION,
    DEFAULT_FFT_SIZE,
    DEFAULT_MIN_DB,
    PitchTrackerSettingsDialog,
)
from friture.plotting.coordinateTransform import CoordinateTransform
import friture.plotting.frequency_scales as fscales
from friture.ringbuffer import RingBuffer
from friture.scope_data import Scope_Data
from friture.store import GetStore
from friture.qml_tools import qml_url, raise_if_error


def frequency_to_note(freq: float) -> str:
    if np.isnan(freq) or freq <= 0:
        return ""
    # number of semitones from C4
    # A4 = 440Hz and is 9 semitones above C4
    semitone = round(np.log2(freq/440) * 12) + 9
    octave = int(np.floor(semitone / 12)) + 4
    notes = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"]
    return f'{notes[semitone % 12]}{octave}'

def format_frequency(freq: float) -> str:
    if freq < 1000:
        return f'{freq:.0f} Hz ({frequency_to_note(freq)})'
    else:
        return f'{freq/1000:.1f} kHz ({frequency_to_note(freq)})'


class PitchTrackerWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget, engine: QQmlEngine):
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)

        self.setObjectName("PitchTracker_Widget")

        store = GetStore()
        self._pitch_tracker_data = Scope_Data(store)
        store._dock_states.append(self._pitch_tracker_data)
        state_id = len(store._dock_states) - 1

        self._curve = Curve()
        self._curve.name = "Ch1" # type: ignore [assignment]
        self._pitch_tracker_data.add_plot_item(self._curve)

        # cast for qt properties which aren't properly typed
        tracker_data: Any = self._pitch_tracker_data
        tracker_data.vertical_axis.name = "Frequency (Hz)"
        tracker_data.vertical_axis.setTrackerFormatter(
            format_frequency)
        tracker_data.vertical_axis.show_minor_grid_lines = True
        tracker_data.horizontal_axis.name = "Time (sec)"
        tracker_data.horizontal_axis.setTrackerFormatter(
            lambda x: "%#.3g sec" % (x))

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(2, 2, 2, 2)

        self.quickWidget = QQuickWidget(engine, self)
        self.quickWidget.statusChanged.connect(self.on_status_changed)
        self.quickWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.quickWidget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.quickWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.quickWidget.setSource(qml_url("Scope.qml"))

        raise_if_error(self.quickWidget)

        root: Any = self.quickWidget.rootObject()
        root.setProperty("stateId", state_id)

        self.gridLayout.addWidget(self.quickWidget, 0, 0, 1, 1)

        self.pitch_view_model = PitchViewModel(self)
        pitch_window = QQuickWindow()
        pitch_component = QQmlComponent(engine, qml_url("PitchView.qml"), self)
        raise_if_error(pitch_component)
        pitch_object: Any = pitch_component.createWithInitialProperties(
            {
                "parent": pitch_window.contentItem(),
                "pitch_view_model": self.pitch_view_model
            },
            engine.rootContext()
        )
        pitch_object.setParent(pitch_window)
        pitch_widget = QtWidgets.QWidget.createWindowContainer(pitch_window, self)
        pitch_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        pitch_widget.setFixedWidth(int(pitch_object.width()))
        self.gridLayout.addWidget(pitch_widget, 0, 1)

        self.min_freq = DEFAULT_MIN_FREQ
        self.max_freq = DEFAULT_MAX_FREQ
        self._pitch_tracker_data.vertical_axis.setRange( # type: ignore
            self.min_freq, self.max_freq)
        self._pitch_tracker_data.vertical_axis.setScale( # type: ignore
            fscales.Octave)
        self.vertical_transform = CoordinateTransform(
            self.min_freq, self.max_freq, 1, 0, 0)
        self.vertical_transform.setScale(fscales.Octave)

        self.duration = DEFAULT_DURATION
        self._pitch_tracker_data.horizontal_axis.setRange( # type: ignore
            -self.duration, 0.)

        self.settings_dialog = PitchTrackerSettingsDialog(self)

        self.audiobuffer: Optional[AudioBuffer] = None
        self.tracker = PitchTracker(RingBuffer())
        self.update_curve()


    # method
    def set_buffer(self, buffer: AudioBuffer) -> None:
        self.audiobuffer = buffer
        self.tracker.set_input_buffer(buffer.ringbuffer)

    def handle_new_data(self, floatdata: np.ndarray) -> None:
        if self.tracker.update():
            self.update_curve()
            self.pitch_view_model.pitch = self.tracker.get_latest_estimate() # type: ignore

    def update_curve(self) -> None:
        pitches = self.tracker.get_estimates(self.duration)
        pitches = 1.0 - self.vertical_transform.toScreen(pitches) # type: ignore
        pitches = np.clip(pitches, 0, 1)
        times = np.linspace(0, 1.0, pitches.shape[0])
        self._curve.setData(times, pitches)

    def on_status_changed(self, status: QQuickWidget.Status) -> None:
        if status == QQuickWidget.Error:
            for error in self.quickWidget.errors():
                self.logger.error("QML error: " + error.toString())

    # method
    def canvasUpdate(self) -> None:
        # nothing to do here
        return

    def set_min_freq(self, value: int) -> None:
        self.min_freq = value
        self._pitch_tracker_data.vertical_axis.setRange(self.min_freq, self.max_freq) # type: ignore
        self.vertical_transform.setRange(self.min_freq, self.max_freq)

    def set_max_freq(self, value: int) -> None:
        self.max_freq = value
        self._pitch_tracker_data.vertical_axis.setRange(self.min_freq, self.max_freq) # type: ignore
        self.vertical_transform.setRange(self.min_freq, self.max_freq)

    def set_duration(self, value: int) -> None:
        self.duration = value
        self._pitch_tracker_data.horizontal_axis.setRange(-self.duration, 0.) # type: ignore

    def set_min_db(self, value: float) -> None:
        self.tracker.min_db = value

    # slot
    def settings_called(self, checked: bool) -> None:
        self.settings_dialog.show()

    # method
    def saveState(self, settings: QSettings) -> None:
        self.settings_dialog.save_state(settings)

    # method
    def restoreState(self, settings: QSettings) -> None:
        self.settings_dialog.restore_state(settings)


class PitchViewModel(QObject):
    pitch_changed = pyqtSignal(float)

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self._pitch = 0.0

    @pyqtProperty(str, notify=pitch_changed)
    def pitch(self) -> str:
        if not self._pitch or np.isnan(self._pitch):
            return '--'
        elif self._pitch < 1000:
            return f"{self._pitch:.0f}"
        else:
            return f"{self._pitch/1000:.2f}"

    @pitch.setter # type: ignore
    def pitch(self, pitch: float):
        self._pitch = pitch
        self.pitch_changed.emit(pitch)

    @pyqtProperty(str, notify=pitch_changed) # type: ignore
    def pitch_unit(self) -> str:
        if self._pitch >= 1000.0:
            return "kHz"
        else:
            return "Hz"

    @pyqtProperty(str, notify=pitch_changed) # type: ignore
    def note(self) -> str:
        if not self._pitch or np.isnan(self._pitch):
            return '--'
        else:
            return frequency_to_note(self._pitch)


class PitchTracker:
    def __init__(
        self,
        input_buf: RingBuffer,
        fft_size: int = DEFAULT_FFT_SIZE,
        overlap: float = 0.75,
        sample_rate: int = SAMPLING_RATE,
        min_db: float = DEFAULT_MIN_DB,
    ):
        self.fft_size = fft_size
        self.overlap = overlap
        self.sample_rate = sample_rate
        self.min_db = min_db

        self.input_buf = input_buf
        self.input_buf.grow_if_needed(fft_size)
        self.next_in_offset = self.input_buf.offset

        self.out_buf = RingBuffer()
        self.out_offset = self.out_buf.offset

        self.proc = audioproc()
        self.proc.set_fftsize(self.fft_size)

    def set_input_buffer(self, new_buf: RingBuffer) -> None:
        self.input_buf = new_buf
        self.input_buf.grow_if_needed(self.fft_size)
        self.next_in_offset = self.input_buf.offset

    def update(self) -> bool:
        new = [self.estimate_pitch(f) for f in self.new_frames()]
        self.out_buf.push(np.array([new]))
        self.out_offset = self.out_buf.offset
        return len(new) != 0

    def get_estimates(self, time_s: float) -> np.ndarray:
        step_size = m.floor(self.fft_size * (1.0 - self.overlap))
        num_results = m.floor(time_s / (step_size / self.sample_rate)) + 1
        return self.out_buf.data_indexed(self.out_offset, num_results)[0,:]

    def get_latest_estimate(self) -> float:
        return self.out_buf.data_indexed(self.out_offset, 1)[0,0]

    def new_frames(self) -> Generator[np.ndarray, None, None]:
        assert self.input_buf.offset >= self.next_in_offset
        while self.next_in_offset + self.fft_size <= self.input_buf.offset:
            # data_indexed is (end_index, length) for some reason
            yield self.input_buf.data_indexed(
                self.next_in_offset + self.fft_size, self.fft_size)
            self.next_in_offset += m.floor(self.fft_size * (1.0 - self.overlap))

    def estimate_pitch(self, frame: np.ndarray) -> Optional[float]:
        spectrum = np.abs(np.fft.rfft(frame[0, :] * self.proc.window))

        # Compute harmonic product spectrum; the frequency with the largest
        # value is quite likely to be a fundamental frequency.
        # Chose 3 harmonics for no particularly good reason; empirically this
        # seems reasonably effective.
        product_count = 3
        harmonic_length = spectrum.shape[0] // product_count
        hps = spectrum[:harmonic_length]
        for i in range(2, product_count + 1):
            hps *= spectrum[::i][:harmonic_length]

        pitch_idx = np.argmax(hps)
        if pitch_idx == 0:
            # This should only occur if the HPS is all zero. No pitch, don't
            # try to take the log of zero.
            return None

        # Compute dB for the detected fundamental; if it's too low presume it's
        # a false detection and return no result.
        db = 10 * np.log10(spectrum[pitch_idx] ** 2 / self.fft_size ** 2)
        if db < self.min_db:
            return None
        else:
            return self.proc.freq[pitch_idx]
