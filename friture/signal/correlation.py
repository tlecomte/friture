#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2018 Timothée Lecomte

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

import numpy
from numpy.fft import rfft, irfft


def generalized_cross_correlation(d0, d1):
    # substract the means
    # (in order to get a normalized cross-correlation at the end)
    d0 -= d0.mean()
    d1 -= d1.mean()

    # Hann window to mitigate non-periodicity effects
    window = numpy.hanning(len(d0))

    # compute the cross-correlation
    D0 = rfft(d0 * window)
    D1 = rfft(d1 * window)
    D0r = D0.conjugate()
    G = D0r * D1
    absG = numpy.abs(G)
    m = max(absG)
    W = 1. / (1e-10 * m + absG)  # weight for a normalized "PHAT" cross-correlation
    Xcorr = irfft(W * G)

    return Xcorr
