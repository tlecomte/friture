#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Timothée Lecomte

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

from PyQt5.QtCore import pyqtSignal, pyqtProperty, QRectF
from PyQt5.QtQuick import QQuickPaintedItem
from PyQt5.QtGui import QPainter
from friture.audiobackend import AudioBackend
from friture.spectrogram_item_data import SpectrogramImageData

# QQuickPaintedItem does not work for all Qt backends.
# Ideally we would use QSGSimpleTextureNode and createTextureFromImage instead,
# but I did not manage to fix the segfaults that I got with those
# To revist in Qt6
class SpectrogramItem(QQuickPaintedItem):
    curveChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAntialiasing(True)

        self._curve = SpectrogramImageData()

    @pyqtProperty(SpectrogramImageData, notify=curveChanged)
    def curve(self) -> SpectrogramImageData:
        return self._curve

    @curve.setter
    def curve(self, curve: SpectrogramImageData) -> None:
        if self._curve != curve:
            self._curve = curve
            curve.data_changed.connect(self.update)
            curve.data_changed.connect(self.updateScreenSize)
            self.curveChanged.emit()
            if self.window():
                self.window().update()

    def updateScreenSize(self) -> None:
        self._curve.update_screen_size(self.width(), self.height())

    def paint(self, painter: QPainter) -> None:
        if self._curve.is_playing:
            self.last_paint_time = AudioBackend().get_stream_time()
        
        pixmap_source_rect = self._curve.pixmap_source_rect(self.last_paint_time)

        painter.drawPixmap(
            QRectF(0, 0, self.width(), self.height()),
            self._curve.pixmap(),
            pixmap_source_rect)