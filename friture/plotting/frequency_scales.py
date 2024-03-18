#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2021 Clo Yun-Hee Dufour

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

from __future__ import annotations # to use built-in types in annotations before Python 3.9
from typing import List, Union, Tuple
from math import ceil, floor
from decimal import Decimal
import numpy as np

def numberPrecision(x):
    return Decimal(x).adjusted()


def ceilWithPrecision(x, prec):
    return ceil(x * 10 ** -(prec)) * 10 ** (prec)


def floorWithPrecision(x, prec):
    return floor(x * 10 ** -(prec)) * 10 ** (prec)


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

    i = np.argmin(distances)

    return candidates[i]


class Linear(object):
    NAME = 'Linear'

    @staticmethod
    def transform(frequency: float) -> float :
        # No transformation is applied
        return frequency
    
    @staticmethod
    def inverse(value: float) -> float :
        # No transformation is applied
        return value

    @staticmethod
    def ticks(scale_min, scale_max) -> tuple[list[float], list[float]] :
        trueMin = min(scale_min, scale_max)
        trueMax = max(scale_min, scale_max)

        major_ticks, major_tick_interval = Linear._majorTicks(trueMin, trueMax)

        if len(major_ticks) < 2:
            minor_ticks = []
        else:
            minor_ticks = Linear._minorTicks(trueMin, trueMax, major_ticks[0], major_tick_interval)

        return major_ticks, minor_ticks

    @staticmethod
    def _majorTicks(trueMin, trueMax) -> tuple[list[float], float] :
        rang = trueMax - trueMin
        base_interval = rang / 6.
        approx_interval_prec = numberPrecision(base_interval)
        approx_interval = roundWithPrecision(base_interval, approx_interval_prec)
        rmin = ceilWithinInterval(trueMin, approx_interval)

        if approx_interval == 0:
            return [], 0

        # add ticks up to the max
        N = int(floor((trueMax - rmin) / approx_interval))
        ticks = [rmin + approx_interval * i for i in range(N + 1)]
        
        return ticks, approx_interval

    @staticmethod
    def _minorTicks(trueMin, trueMax, firstMajorTick, majorTickInterval) -> list[float] :
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
        x = firstMajorTick
        while x >= trueMin:
            x -= minorTickInterval
        x += minorTickInterval

        # fill up to the max
        ticks = []
        while x <= trueMax:
            ticks.append(x)
            x += minorTickInterval

        return ticks

def freq_to_note(freq: float) -> str:
    if np.isnan(freq) or freq <= 0:
        return ""
    # number of semitones from C4
    # A4 = 440Hz and is 9 semitones above C4
    semitone = round(np.log2(freq/440) * 12) + 9
    octave = int(np.floor(semitone / 12)) + 4
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f'{notes[semitone % 12]}{octave}'

class Logarithmic(object):
    NAME = 'Logarithmic'

    @staticmethod
    def transform(frequency: float) -> float :
        return np.log10(frequency)
    
    @staticmethod
    def inverse(logs: float) -> float :
        return 10 ** logs

    @staticmethod
    def ticks(scale_min, scale_max) -> tuple[list[float], list[float]] :
        trueMin = min(scale_min, scale_max)
        trueMax = max(scale_min, scale_max)

        if trueMin <= 0.:
            trueMin = 1e-20
            trueMax = max(trueMax, trueMin)

        trueMinLog10 = np.log10(trueMin)
        trueMaxLog10 = np.log10(trueMax)

        trueMinLog10Ceil = int(ceil(trueMinLog10))
        trueMaxLog10Floor = int(floor(trueMaxLog10))

        majorTicks = [10 ** i for i in range(trueMinLog10Ceil, trueMaxLog10Floor + 1)]
        
        minorTicks = []
        
        if len(majorTicks) >= 2:
            standardLogTicks = [2, 3, 4, 5, 6, 7, 8, 9]

            for a in standardLogTicks:
                if a * majorTicks[0] / 10. >= trueMin:
                    minorTicks.append(a * majorTicks[0] / 10.)

            minorTicks += [a * x for a in standardLogTicks for x in majorTicks]

            for a in standardLogTicks:
                if a * majorTicks[-1] <= trueMax:
                    minorTicks.append(a * majorTicks[-1])

        return majorTicks, minorTicks


class Octave(object):
    '''
    A log2 scale with major ticks at the A of each octave, and minor ticks each
    minor third, which is useful when analysing pitch.
    '''
    NAME = 'Octave'

    @staticmethod
    def transform(frequency: float) -> float:
        return np.log2(frequency)

    @staticmethod
    def inverse(logs: float) -> float:
        return 2 ** logs

    @staticmethod
    def ticks(scale_min, scale_max) -> Tuple[List[float], List[float]]:
        if scale_min > scale_max:
            scale_min, scale_max = (scale_max, scale_min)
        scale_min = max(1e-20, scale_min)
        scale_max = max(1e-20, scale_max)

        # Relative to A4 = 440Hz
        min_A = ceil(np.log2(scale_min / 440))
        max_A = floor(np.log2(scale_max / 440))
        major_ticks = [ 440 * (2 ** i) for i in range(min_A, max_A + 1)]

        thirds = np.power(2, [3/12, 6/12, 9/12])
        minor_ticks = [440 * (2 ** a) * t
            for a in range(min_A - 1, max_A + 1)
            for t in thirds]
        minor_ticks = [t for t in minor_ticks
            if t >= scale_min and t <= scale_max]

        return major_ticks, minor_ticks


class Mel(object):
    NAME = 'Mel'

    @staticmethod
    def transform(frequency: float) -> float :
        return 2595 * np.log10(1 + frequency / 700)
    
    @staticmethod
    def inverse(mels: float) -> float :
        return 700 * (10 ** (mels / 2595) - 1)

    @staticmethod
    def ticks(scale_min, scale_max) -> tuple[list[float], list[float]] :
        return Logarithmic.ticks(scale_min, scale_max)

        
class Erb(object):
    NAME = 'ERB'

    A = 21.33228113095401739888262

    @staticmethod
    def transform(frequency: float) -> float :
        return Erb.A * np.log10(1 + 0.00437 * frequency)
    
    @staticmethod
    def inverse(erbs: float) -> float :
        return (10 ** (erbs / Erb.A) - 1) / 0.00437

    @staticmethod
    def ticks(scale_min, scale_max) -> tuple[list[float], list[float]] :
        return Logarithmic.ticks(scale_min, scale_max)


ALL = [Linear, Logarithmic, Mel, Erb, Octave]