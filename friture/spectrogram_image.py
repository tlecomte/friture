#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

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

import numpy
from PyQt5 import QtCore, QtGui


class CanvasScaledSpectrogram(QtCore.QObject):
    """
    A 2D image that is meant to hold the spectrogram data, in a ringbuffer-style.

    Architecture:
    1. quickly convert each piece of data to a pixmap,
    (with the right pixel size, since QImage to QPixmap conversion is slow, and scaling is slow too)
    2. use a cache of size M=2*N
    3. write in the cache at the position j and j+N
    4. the data part that is to be drawn can be read contiguously from j+1 to j+1+N
    """
    canvasWidthChanged = QtCore.pyqtSignal(int)

    def __init__(self, canvas_height=2, canvas_width=2):
        super().__init__()

        self.logger = logging.getLogger(__name__)

        self.canvas_height = canvas_height
        self.canvas_width = canvas_width

        self.pixmap = QtGui.QPixmap(2 * self.canvas_width, self.canvas_height)
        # print("pixmap info : hasAlpha =", self.pixmap.hasAlpha(), ", depth =", self.pixmap.depth(), ", default depth =", self.pixmap.defaultDepth())
        self.pixmap.fill(QtGui.QColor("black"))
        self.painter = QtGui.QPainter()
        self.write_offset = 0
        self.last_write_time = 0

    def erase(self):
        self.pixmap = QtGui.QPixmap(2 * self.canvas_width, self.canvas_height)
        self.pixmap.fill(QtGui.QColor("black"))
        self.write_offset = 0

    # resize the pixmap and update the offsets accordingly
    def resize(self, width, height):
        oldWidth = int(self.pixmap.width() / 2)
        if width != oldWidth:
            self.write_offset = (self.write_offset % oldWidth) * width / oldWidth
            self.write_offset = self.write_offset % width  # to handle negative values
        self.pixmap = self.pixmap.scaled(2 * width, height, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)

    def setcanvas_height(self, canvas_height):
        if self.canvas_height != int(canvas_height):
            self.canvas_height = int(canvas_height)
            self.resize(self.canvas_width, self.canvas_height)
            self.logger.info("Spectrogram image: canvas_height changed, now: %d", int(canvas_height))

    def setcanvas_width(self, canvas_width):
        if self.canvas_width != int(canvas_width):
            self.canvas_width = int(canvas_width)
            self.resize(self.canvas_width, self.canvas_height)
            self.canvasWidthChanged.emit(int(canvas_width))
            self.logger.info("Spectrogram image: canvas_width changed, now: %d", int(canvas_width))

    def addData(self, xyzs: numpy.ndarray, last_data_time: float) -> None:
        # revert the frequency axis so that the larger frequencies
        # are at the top of the widget
        xyzs = xyzs[::-1, :]

        width = xyzs.shape[1]

        # convert the data to colors, and then to a data string
        # that QImage can understand
        byteString = self.colors_to_bytes(xyzs)

        myimage = self.prepare_image(byteString, width, xyzs.shape[0])

        # Now, draw the image onto the widget pixmap, which has
        # the structure of a 2D ringbuffer

        offset = self.write_offset % self.canvas_width

        # first copy, always complete
        source1 = QtCore.QRectF(0, 0, width, xyzs.shape[0])
        target1 = QtCore.QRectF(offset, 0, width, xyzs.shape[0])
        # second copy, can be folded
        direct = min(width, self.canvas_width - offset)
        folded = width - direct
        source2a = QtCore.QRectF(0, 0, direct, xyzs.shape[0])
        target2a = QtCore.QRectF(offset + self.canvas_width, 0, direct, xyzs.shape[0])
        source2b = QtCore.QRectF(direct, 0, folded, xyzs.shape[0])
        target2b = QtCore.QRectF(0, 0, folded, xyzs.shape[0])

        self.painter.begin(self.pixmap)
        self.painter.drawImage(target1, myimage, source1)
        self.painter.drawImage(target2a, myimage, source2a)
        self.painter.drawImage(target2b, myimage, source2b)
        self.painter.end()

        # updating the offset
        self.write_offset += width
        self.last_write_time = last_data_time

    def colors_to_bytes(self, data):
        return data.tobytes()

    # defined as a separate function so that it appears in the profiler
    # NOTE: QImage with a colormap is slower (by a factor of 2) than the custom
    # colormap code here.
    def prepare_image(self, byteString, width, height):
        myimage = QtGui.QImage(byteString, width, height, QtGui.QImage.Format_RGB32)
        return myimage

    def getpixmap(self):
        return self.pixmap

    def getpixmapoffset(self, read_time: float, canvas_timerange: float) -> float:        
        read_write_time_delay = read_time - self.last_write_time
        read_write_pixel_delay = self.canvas_width * read_write_time_delay / canvas_timerange
        return (self.write_offset + read_write_pixel_delay) % self.canvas_width
