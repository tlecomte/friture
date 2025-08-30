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

import logging

from PyQt5.QtCore import pyqtSignal, QObject

from friture.playback.playback_control_view_model import PlaybackControlViewModel
from friture.playback.player import Player

logger = logging.getLogger(__name__)

class PlaybackControlWidget(QObject):
    recording_toggled = pyqtSignal(bool)

    def __init__(self, parent: QObject, player: Player, playback_control_view_model: PlaybackControlViewModel) -> None:
        super().__init__(parent)

        self._playback_control_view_model = playback_control_view_model

        self._playback_control_view_model.recording_changed.connect(self.on_recording_changed)
        self._playback_control_view_model.playing_changed.connect(self.on_playing_changed)
        self._playback_control_view_model.position_changed.connect(self.on_playback_position_changed)

        self.player = player
        self.player.stopped.connect(self.on_playback_stopped)
        self.player.recorded_length_changed.connect(self.on_recorded_len_changed)
        self.player.playback_time_changed.connect(self.on_playback_time_changed)

    def start_recording(self) -> None:
        if not self.player.is_stopped():
            self.player.stop()
        self._playback_control_view_model.set_playing(False)
        self._playback_control_view_model.set_recording(True)

    def stop_recording(self) -> None:
        self._playback_control_view_model.set_playing(False)
        self._playback_control_view_model.set_recording(False)

    def on_recording_changed(self, recording: bool) -> None:
        self.recording_toggled.emit(recording)

    def on_playing_changed(self, playing: bool) -> None:
        if playing:
            self.player.play()
        else:
            self.player.stop()

    def on_playback_stopped(self) -> None:
        self._playback_control_view_model.set_playing(False)
        self._playback_control_view_model.set_position(self.player.play_start_time)

    def on_playback_position_changed(self, value: float) -> None:
        self.player.play_start_time = value

    def on_recorded_len_changed(self, length: float) -> None:
        # Always give the slider a nonzero length even if nothing is recorded
        self._playback_control_view_model.set_recording_start_time(-max(length, 0.1))

    def on_playback_time_changed(self, time: float) -> None:
        self._playback_control_view_model.set_position(time)
