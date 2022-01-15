#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth￩e Lecomte

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

from PyQt5 import Qt
from numpy import array
import numpy as np

class HistogramPeakBarItem:

    def __init__(self, *args):
        self.fl = [0.]
        self.fh = [0.]
        self.peaks = array([0.])
        self.palette_index = [0]
        self.y = array([0.])
        self.canvas_width = 2
        self.need_transform = False
        self.y_map = None

        self.palette = [Qt.QColor(255, gb, gb) for gb in range(0, 256)]

    def setData(self, fl, fh, peaks, peaks_int, y):
        if len(self.peaks) != len(peaks):
            self.fl = fl
            self.fh = fh
            self.need_transform = True

        self.peaks = peaks
        self.palette_index = (255 * (1. - peaks_int)).astype(int)
        self.y = array(y)

    def draw(self, painter, x_map, y_map, rect):
        # update the cache according to possibly new canvas dimensions
        h = rect.height()
        w = rect.width()
        if w != self.canvas_width:
            self.canvas_width = w
            self.need_transform = True

        if self.need_transform:
            # round to pixels
            self.x1 = np.round(x_map.toScreen(array(self.fl)))
            self.x2 = np.round(x_map.toScreen(array(self.fh)))

            self.need_transform = False

        peaks = h - y_map.toScreen(self.peaks)
        ys = h - y_map.toScreen(self.y)

        for x1, x2, peak, index, y in zip(self.x1, self.x2, peaks, self.palette_index, ys):
            painter.fillRect(x1, peak, x2 - x1, y - peak + 1, self.palette[index])
