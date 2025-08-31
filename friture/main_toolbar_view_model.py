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
from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot

class MainToolbarViewModel(QtCore.QObject):
    recording_changed = pyqtSignal(bool)
    recording_clicked = pyqtSignal()
    new_dock_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    about_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._recording = True
    
    def get_recording(self) -> bool:
        return self._recording
    
    def set_recording(self, recording: bool) -> None:
        if self._recording != recording:
            self._recording = recording
            self.recording_changed.emit(recording)
    
    recording = pyqtProperty(bool, fget=get_recording, fset=set_recording, notify=recording_changed)
    
    @pyqtSlot()
    def recording_toggle(self) -> None:
        self.recording_clicked.emit()

    @pyqtSlot()
    def new_dock(self) -> None:
        self.new_dock_clicked.emit()
    
    @pyqtSlot()
    def settings(self) -> None:
        self.settings_clicked.emit()
    
    @pyqtSlot()
    def about(self) -> None:
        self.about_clicked.emit()
