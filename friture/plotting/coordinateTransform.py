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

import numpy as np

# transforms between screen coordinates and plot coordinates


class CoordinateTransform(object):

    def __init__(self, coord_min, coord_max, length, startBorder, endBorder):
        super(CoordinateTransform, self).__init__()

        self.coord_min = coord_min
        self.coord_max = coord_max
        self.length = length
        self.startBorder = startBorder
        self.endBorder = endBorder
        self.log = False

    def setRange(self, coord_min, coord_max):
        self.coord_min = coord_min
        self.coord_max = coord_max

    def setLength(self, length):
        self.length = length

    def setBorders(self, start, end):
        self.startBorder = start
        self.endBorder = end

    def setLinear(self):
        self.log = False

    def setLogarithmic(self):
        self.log = True

    def toScreen(self, x):
        if self.log:
            logMin = max(1e-20, self.coord_min)
            logMax = max(logMin, self.coord_max)

            if logMin == logMax:
                return self.startBorder + 0. * x  # keep x type (this can produce a RunTimeWarning if x contains inf)

            x = (x < 1e-20) * 1e-20 + (x >= 1e-20) * x
            return (np.log10(x / logMin)) * (self.length - self.startBorder - self.endBorder) / np.log10(logMax / logMin) + self.startBorder
        else:
            if self.coord_max == self.coord_min:
                return self.startBorder + 0. * x  # keep x type (this can produce a RunTimeWarning if x contains inf)

            return (x - self.coord_min) * (self.length - self.startBorder - self.endBorder) / (self.coord_max - self.coord_min) + self.startBorder

    def toPlot(self, x):
        if self.length == self.startBorder + self.endBorder:
            return self.coord_min + 0. * x  # keep x type (this can produce a RunTimeWarning if x contains inf)

        if self.log:
            return 10 ** ((x - self.startBorder) * np.log10(self.coord_max / self.coord_min) / (self.length - self.startBorder - self.endBorder)) * self.coord_min
        else:
            return (x - self.startBorder) * (self.coord_max - self.coord_min) / (self.length - self.startBorder - self.endBorder) + self.coord_min
