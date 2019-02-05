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
from friture.plotting import generated_cmrmap
from friture_extensions.lookup_table import pyx_color_from_float_2D


class CanvasScaledSpectrogram(QtCore.QObject):
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
        self.offset = 0
        self.time_offset = 0

        # prepare a custom colormap
        self.prepare_palette()

        # performance timer
        self.time = QtCore.QTime()
        self.time.start()
        # self.logfile = open("latency_log.txt",'w')

        self.resetBound = 20

    def erase(self):
        self.pixmap = QtGui.QPixmap(2 * self.canvas_width, self.canvas_height)
        self.pixmap.fill(QtGui.QColor("black"))
        self.offset = 0
        self.time_offset = 0

    # resize the pixmap and update the offsets accordingly
    def resize(self, width, height):
        oldWidth = self.pixmap.width() / 2
        if width != oldWidth:
            self.offset = (self.offset % oldWidth) * width / oldWidth
            self.offset = self.offset % width  # to handle negative values
            self.time_offset = (self.time_offset % oldWidth) * width / oldWidth
        self.pixmap = self.pixmap.scaled(2 * width, height, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)

    def setcanvas_height(self, canvas_height):
        if self.canvas_height != canvas_height:
            self.canvas_height = canvas_height
            self.resize(self.canvas_width, self.canvas_height)
            self.logger.info("Spectrogram image: canvas_height changed, now: %d", canvas_height)

    def setcanvas_width(self, canvas_width):
        if self.canvas_width != canvas_width:
            self.canvas_width = canvas_width
            self.resize(self.canvas_width, self.canvas_height)
            self.canvasWidthChanged.emit(canvas_width)
            self.logger.info("Spectrogram image: canvas_width changed, now: %d", canvas_width)

    def addPixelAdvance(self, pixel_advance):
        self.time_offset += pixel_advance

        # avoid long-run drift between self.offset and self.time_offset
        alpha = 0.98
        self.time_offset = alpha * self.time_offset + (1. - alpha) * self.offset

    def addData(self, xyzs):
        # revert the frequency axis so that the larger frequencies
        # are at the top of the widget
        xyzs = xyzs[::-1, :]

        width = xyzs.shape[1]

        # convert the data to colors, and then to a data string
        # that QImage can understand
        byteString = self.floats_to_bytes(xyzs)

        myimage = self.prepare_image(byteString, width, xyzs.shape[0])

        # Now, draw the image onto the widget pixmap, which has
        # the structure of a 2D ringbuffer

        offset = self.offset % self.canvas_width

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
        self.offset += width

    def floats_to_bytes(self, data):
        # dat1 = (255. * data).astype(numpy.uint8)
        # dat4 = dat1.repeat(4)

        dat4 = self.color_from_float(data)
        return dat4.tostring()

    # defined as a separate function so that it appears in the profiler
    # NOTE: QImage with a colormap is slower (by a factor of 2) than the custom
    # colormap code here.
    def prepare_image(self, byteString, width, height):
        myimage = QtGui.QImage(byteString, width, height, QtGui.QImage.Format_RGB32)
        return myimage

    def prepare_palette(self):
        self.logger.info("palette preparation")

        cmap = generated_cmrmap.CMAP

        self.colors = numpy.zeros((cmap.shape[0]), dtype=numpy.uint32)

        for i in range(cmap.shape[0]):
            self.colors[i] = QtGui.QColor(cmap[i, 0] * 255, cmap[i, 1] * 255, cmap[i, 2] * 255).rgb()

    def color_from_float(self, v):
        # clip in [0..1] before using the fast lookup function
        v = numpy.clip(v, 0., 1.)
        return pyx_color_from_float_2D(self.colors, v)
        # d = (v*255).astype(numpy.uint8)
        # return self.colors[d]

    # def interpolate_colors(colors, flat=False, num_colors=256):
        # colors =
        # """ given a list of colors, create a larger list of colors interpolating
        # the first one. If flatten is True a list of numers will be returned. If
        # False, a list of (r,g,b) tuples. num_colors is the number of colors wanted
        # in the final list """

        # palette = []

        # for i in range(num_colors):
        # index = (i * (len(colors) - 1))/(num_colors - 1.0)
        # index_int = int(index)
        # alpha = index - float(index_int)

        # if alpha > 0:
        # r = (1.0 - alpha) * colors[index_int][0] + alpha * colors[index_int + 1][0]
        # g = (1.0 - alpha) * colors[index_int][1] + alpha * colors[index_int + 1][1]
        # b = (1.0 - alpha) * colors[index_int][2] + alpha * colors[index_int + 1][2]
        # else:
        # r = (1.0 - alpha) * colors[index_int][0]
        # g = (1.0 - alpha) * colors[index_int][1]
        # b = (1.0 - alpha) * colors[index_int][2]

        # if flat:
        # palette.extend((int(r), int(g), int(b)))
        # else:
        # palette.append((int(r), int(g), int(b)))

        # return palette

    def getpixmap(self):
        return self.pixmap

    def getpixmapoffset(self, delay=0):
        return self.offset % self.canvas_width

    # this is used when there is an underflow in the audio input
    def syncOffsets(self):
        self.time_offset = self.offset

# plan :
# 1. quickly convert each piece of data to a pixmap, with the right pixel size
# as QImage to QPixmap conversion is slow, and scaling is slow too
# 2. use a cache of size M=2*N
# 3. write in the cache at the position j and j+N
# 4. the data part that is to be drawn can be read contiguously from j+1 to j+1+N
