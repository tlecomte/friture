#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad, Timothée Lecomte

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

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal

class PlaybackControlViewModel(QObject):
    recording_changed = pyqtSignal(bool)
    playing_changed = pyqtSignal(bool)
    position_changed = pyqtSignal(float)
    recording_start_time_changed = pyqtSignal(float)

    def __init__(self, parent: QObject):
        super().__init__(parent)

        self._recording = True
        self._playing = False
        self._position = 0.
        self._recording_start_time = -0.1

    def get_recording(self) -> bool:
        return self._recording

    def set_recording(self, recording: bool) -> None:
        if self._recording != recording:
            self._recording = recording
            self.recording_changed.emit(recording)

    recording = pyqtProperty(bool, fget=get_recording, fset=set_recording, notify=recording_changed)

    def get_playing(self) -> bool:
        return self._playing

    def set_playing(self, playing: bool) -> None:
        if self._playing != playing:
            self._playing = playing
            self.playing_changed.emit(playing)

    playing = pyqtProperty(bool, fget=get_playing, fset=set_playing, notify=playing_changed)

    def get_position(self) -> float:
        return self._position

    def set_position(self, position: float) -> None:
        if self._position != position:
            self._position = position
            self.position_changed.emit(position)

    position = pyqtProperty(float, fget=get_position, fset=set_position, notify=position_changed)

    def get_recording_start_time(self) -> float:
        return self._recording_start_time

    def set_recording_start_time(self, recording_start_time: float) -> None:
        if self._recording_start_time != recording_start_time:
            self._recording_start_time = recording_start_time
            self.recording_start_time_changed.emit(recording_start_time)

    recording_start_time = pyqtProperty(float, fget=get_recording_start_time, fset=set_recording_start_time, notify=recording_start_time_changed)
