#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2021 Timothée Lecomte

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
from PyQt5.QtCore import pyqtProperty
import numpy
import math

from friture.spectrogram_image import CanvasScaledSpectrogram

class SpectrogramImageData(QtCore.QObject):
    data_changed = QtCore.pyqtSignal()
    name_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.canvasscaledspectrogram = CanvasScaledSpectrogram()

        self._name = ""
        self._screen_width = 1
        self._screen_height = 1
        self.last_data_time = 0.
        self.T = 1.
        self.jitter_seconds = 0.
        self.is_playing = True

    def push(self, data: numpy.ndarray, last_data_time: float) -> None:
        self.last_data_time = last_data_time

        self.canvasscaledspectrogram.addData(data, last_data_time)

        self.data_changed.emit()
    
    def draw(self):
        self.data_changed.emit()

    def pixmap(self):
        return self.canvasscaledspectrogram.getpixmap()
    
    def pixmap_source_rect(self, paint_time):
        pixmap_offset = self.canvasscaledspectrogram.getpixmapoffset(paint_time - self.jitter_seconds, self.T + self.jitter_seconds)
        return QtCore.QRectF(pixmap_offset, 0, self._screen_width, self._screen_height)
    
    def settimerange(self, timerange_seconds):
        self.T = timerange_seconds

    def set_jitter(self, jitter_seconds: float) -> None:
        self.jitter_seconds = jitter_seconds
        self.canvasscaledspectrogram.setcanvas_width(self._screen_width + self.jitter_pix())

    def jitter_pix(self):
        return math.ceil(self._screen_width * self.jitter_seconds / self.T)

    def erase(self):
        self.canvasscaledspectrogram.erase()
    
    def pause(self):
        self.is_playing = False

    def restart(self):
        self.is_playing = True

    @pyqtProperty(str, notify=name_changed)
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        if self._name != name:
            self._name = name
            self.name_changed.emit(name)

    def screen_width(self):
        return self._screen_width

    def screen_height(self):
        return self._screen_height

    def update_screen_size(self, width, height):
        self._screen_width = int(width)
        self._screen_height = int(height)
        self.canvasscaledspectrogram.setcanvas_width(int(width) + self.jitter_pix())
        self.canvasscaledspectrogram.setcanvas_height(int(height))