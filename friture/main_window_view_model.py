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
    theme_index_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._toolbar_view_model = MainToolbarViewModel(self)
        self._level_view_model = LevelViewModel(self)
        self._playback_control_view_model = PlaybackControlViewModel(self)
        self._playback_control_enabled = False
        self._theme_index = 0  # 0 = System Default, 1 = Light, 2 = Dark

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

    def get_theme_index(self) -> int:
        return self._theme_index

    def set_theme_index(self, index: int) -> None:
        if self._theme_index != index:
            self._theme_index = index
            self.theme_index_changed.emit(index)

    theme_index = pyqtProperty(int, fget=get_theme_index, fset=set_theme_index, notify=theme_index_changed)

    @pyqtProperty(str, notify=theme_index_changed)
    def window_color(self) -> str:
        from PyQt5.QtWidgets import QApplication
        return QApplication.instance().palette().window().color().name()

    @pyqtProperty(str, notify=theme_index_changed)
    def window_text_color(self) -> str:
        from PyQt5.QtWidgets import QApplication
        return QApplication.instance().palette().windowText().color().name()

    @pyqtProperty(str, notify=theme_index_changed)
    def base_color(self) -> str:
        from PyQt5.QtWidgets import QApplication
        return QApplication.instance().palette().base().color().name()

    @pyqtProperty(str, notify=theme_index_changed)
    def text_color(self) -> str:
        from PyQt5.QtWidgets import QApplication
        return QApplication.instance().palette().text().color().name()

    @pyqtProperty(str, notify=theme_index_changed)
    def button_color(self) -> str:
        from PyQt5.QtWidgets import QApplication
        return QApplication.instance().palette().button().color().name()

    @pyqtProperty(str, notify=theme_index_changed)
    def button_text_color(self) -> str:
        from PyQt5.QtWidgets import QApplication
        return QApplication.instance().palette().buttonText().color().name()
