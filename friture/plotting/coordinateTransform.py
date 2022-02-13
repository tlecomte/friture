#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Timothée Lecomte

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
from PyQt5.QtCore import pyqtSlot
import numpy as np
import friture.plotting.frequency_scales as fscales

# transforms between screen coordinates and plot coordinates


class CoordinateTransform(QtCore.QObject):

    def __init__(self, coord_min, coord_max, length, startBorder, endBorder, parent=None):
        super(CoordinateTransform, self).__init__(parent)

        self.coord_min = coord_min
        self.coord_max = coord_max
        self.coord_clipped_min = max(1e-20, self.coord_min)
        self.coord_clipped_max = max(self.coord_clipped_min, self.coord_max)
        self.coord_ratio_log = np.log10(self.coord_clipped_max / self.coord_clipped_min)

        self.length = length
        self.startBorder = startBorder
        self.endBorder = endBorder
        self.scale = fscales.Linear

    def setRange(self, coord_min, coord_max):
        self.coord_min = coord_min
        self.coord_max = coord_max
        self.coord_clipped_min = max(1e-20, self.coord_min)
        self.coord_clipped_max = max(self.coord_clipped_min, self.coord_max)
        self.coord_ratio_log = np.log10(self.coord_clipped_max / self.coord_clipped_min)

    def setLength(self, length):
        self.length = length

    def setBorders(self, start, end):
        self.startBorder = start
        self.endBorder = end

    def setScale(self, scale):
        self.scale = scale

    @pyqtSlot(float, result=float)
    def toScreen(self, x):
        if self.scale is fscales.Logarithmic:
            if self.coord_clipped_min == self.coord_clipped_max:
                return self.startBorder + 0. * x  # keep x type (this can produce a RunTimeWarning if x contains inf)

            x = (x < 1e-20) * 1e-20 + (x >= 1e-20) * x
            return (np.log10(x / self.coord_clipped_min)
                    * (self.length - self.startBorder - self.endBorder)
                    / self.coord_ratio_log
                    + self.startBorder)
        else:
            if self.coord_max == self.coord_min:
                return self.startBorder + 0. * x  # keep x type (this can produce a RunTimeWarning if x contains inf)

            trans_x = self.scale.transform(x)
            trans_min = self.scale.transform(self.coord_min)
            trans_max = self.scale.transform(self.coord_max)

            return ((trans_x - trans_min)
                    * (self.length - self.startBorder - self.endBorder)
                    / (trans_max - trans_min)
                    + self.startBorder)

    @pyqtSlot(float, result=float)
    def toPlot(self, x):
        if self.length == self.startBorder + self.endBorder:
            return self.coord_min + 0. * x  # keep x type (this can produce a RunTimeWarning if x contains inf)

        if self.scale is fscales.Logarithmic:
            return 10 ** ((x - self.startBorder) * self.coord_ratio_log / (self.length - self.startBorder - self.endBorder)) * self.coord_min
        else:
            trans_min = self.scale.transform(self.coord_min)
            trans_max = self.scale.transform(self.coord_max)

            trans_x = (x - self.startBorder) * (trans_max - trans_min) / (self.length - self.startBorder - self.endBorder) + trans_min
            return self.scale.inverse(trans_x)
