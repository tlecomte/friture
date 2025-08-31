#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2025 Timothée Lecomte

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

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtProperty, pyqtSignal

from friture.level_view_model import LevelViewModel
from friture.main_toolbar_view_model import MainToolbarViewModel
from friture.playback.playback_control_view_model import PlaybackControlViewModel

class MainWindowViewModel(QtCore.QObject):
    playback_control_enabled_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._toolbar_view_model = MainToolbarViewModel(self)
        self._level_view_model = LevelViewModel(self)
        self._playback_control_view_model = PlaybackControlViewModel(self)
        self._playback_control_enabled = False

    @pyqtProperty(MainToolbarViewModel, constant=True) # type: ignore
    def toolbar_view_model(self):
        return self._toolbar_view_model

    @pyqtProperty(LevelViewModel, constant=True) # type: ignore
    def level_view_model(self):
        return self._level_view_model
    
    @pyqtProperty(PlaybackControlViewModel, constant=True) # type: ignore
    def playback_control_view_model(self):
        return self._playback_control_view_model
    
    def get_playback_control_enabled(self) -> bool:
        return self._playback_control_enabled
    
    def set_playback_control_enabled(self, playback_control_enabled: bool) -> None:
        if self._playback_control_enabled != playback_control_enabled:
            self._playback_control_enabled = playback_control_enabled
            self.playback_control_enabled_changed.emit(playback_control_enabled)
    
    playback_control_enabled = pyqtProperty(int, fget=get_playback_control_enabled, fset=set_playback_control_enabled, notify=playback_control_enabled_changed)
