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

import friture.plotting.frequency_scales as fscales

from friture.plotting.frequency_scales import numberPrecision, ceilWithPrecision, floorWithPrecision

# takes min/max of the scale, and returns appropriate ticks (selected for proper number, rounding)
class ScaleDivision(object):

    def __init__(self, scale_min, scale_max, length):
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.length = length

        self.labelLength = 1

        self.scale = fscales.Linear
        self._update_ticks()

    def set_properties(self, scale_min, scale_max, length):
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.length = length
        self._update_ticks()

    def setRange(self, scale_min, scale_max):
        self.scale_min = scale_min
        self.scale_max = scale_max
        self._update_ticks()

    def setLength(self, length):
        self.length = length

    def setScale(self, scale):
        self.scale = scale
        self._update_ticks()

    def majorTicks(self):
        return self.major_ticks
    
    def minorTicks(self):
        return self.minor_ticks

    def _update_ticks(self):
        self.major_ticks, self.minor_ticks = self.scale.ticks(self.scale_min, self.scale_max)
