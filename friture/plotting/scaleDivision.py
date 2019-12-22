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

import math
from decimal import Decimal
import numpy


def numberPrecision(x):
    return Decimal(x).adjusted()


def ceilWithPrecision(x, prec):
    return math.ceil(x * 10 ** -(prec)) * 10 ** (prec)


def floorWithPrecision(x, prec):
    return math.floor(x * 10 ** -(prec)) * 10 ** (prec)


# 1.1 0.2
# 1.2
def ceilWithinInterval(x, interval):
    prec = numberPrecision(interval)

    candidate = floorWithPrecision(x, prec + 1)

    while candidate < x:
        candidate += interval

    return candidate


# 0.322
# 0.3
# 0.1, 0.2, 0.5
def roundWithPrecision(x, prec):
    candidates = [1. * 10 ** prec, 2. * 10 ** prec, 5. * 10 ** prec]

    # find closest
    distances = [abs(x - candidate) for candidate in candidates]

    i = numpy.argmin(distances)

    return candidates[i]


# takes min/max of the scale, and returns appropriate ticks (selected for proper number, rounding)
class ScaleDivision(object):

    def __init__(self, scale_min, scale_max, length):
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.length = length

        self.majorTickInterval = 0

        self.labelLength = 1

        self.log = False

    def set_properties(self, scale_min, scale_max, length):
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.length = length

    def setRange(self, scale_min, scale_max):
        self.scale_min = scale_min
        self.scale_max = scale_max

    def setLength(self, length):
        self.length = length

    def setLinear(self):
        self.log = False

    def setLogarithmic(self):
        self.log = True

    def majorTicks(self):

        rang = abs(self.scale_max - self.scale_min)
        trueMin = min(self.scale_min, self.scale_max)
        trueMax = max(self.scale_min, self.scale_max)

        if self.log:
            if trueMin <= 0.:
                trueMin = 1e-20
                trueMax = max(trueMax, trueMin)

            trueMinLog10 = numpy.log10(trueMin)
            trueMaxLog10 = numpy.log10(trueMax)

            trueMinLog10Ceil = int(numpy.ceil(trueMinLog10))
            trueMaxLog10Floor = int(numpy.floor(trueMaxLog10))

            ticks = [10 ** i for i in range(trueMinLog10Ceil, trueMaxLog10Floor + 1)]
        else:
            base_interval = rang / 6.

            approx_interval_prec = numberPrecision(base_interval)

            approx_interval = roundWithPrecision(base_interval, approx_interval_prec)

            rmin = ceilWithinInterval(trueMin, approx_interval)

            if approx_interval == 0:
                return []

            # add ticks up to the max
            N = int(math.floor((trueMax - rmin) / approx_interval))
            ticks = [rmin + approx_interval * i for i in range(N + 1)]

            self.majorTickInterval = approx_interval

        return ticks

    def minorTicks(self):
        # subdivide the major ticks intervals, in 5
        majorTicks = self.majorTicks()

        if len(majorTicks) < 2:
            return []

        trueMin = min(self.scale_min, self.scale_max)
        trueMax = max(self.scale_min, self.scale_max)

        if self.log:
            ticks = []

            standardLogTicks = [2, 3, 4, 5, 6, 7, 8, 9]

            for a in standardLogTicks:
                if a * majorTicks[0] / 10. >= trueMin:
                    ticks.append(a * majorTicks[0] / 10.)

            ticks += [a * x for a in standardLogTicks for x in majorTicks]

            for a in standardLogTicks:
                if a * majorTicks[-1] <= trueMax:
                    ticks.append(a * majorTicks[-1])
        else:
            majorTickInterval = self.majorTickInterval

            majorTickIntervalDecimal = Decimal(majorTickInterval)

            mainDigit = majorTickIntervalDecimal.as_tuple().digits[0]

            if mainDigit == 1:
                minorTickDiv = 5
            elif mainDigit == 2:
                minorTickDiv = 4  # could be 2 with another tick subdivision
            elif mainDigit == 5:
                minorTickDiv = 5
            else:
                minorTickDiv = 5

            minorTickInterval = abs(majorTickInterval / minorTickDiv)

            # find lowest bound
            x = majorTicks[0]
            while x >= trueMin:
                x -= minorTickInterval
            x += minorTickInterval

            # fill up to the max
            ticks = []
            while x <= trueMax:
                ticks.append(x)
                x += minorTickInterval

        return ticks
