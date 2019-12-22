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
from friture_extensions.lfilter import pyx_lfilter_float64_1D


def decimate(bdec, adec, x, zi):
    if len(x) == 0:
        raise Exception("Filter input is too small")

    # could use a polyphase decimator here
    x_dec, zf = pyx_lfilter_float64_1D(bdec, adec, x, zi)

    x_dec = x_dec[::2]
    return x_dec, zf


def decimate_multiple(Ndec, bdec, adec, x, zis):
    '''decimate Ndec times'''
    x_dec = x

    # FIXME problems when x is smaller than filter coeff

    # do not run on empty arrays, otherwise output contains artifacts
    if x.size == 0:
        return x, zis

    if zis is None:
        for i in range(Ndec):
            x_dec, zf = decimate(bdec, adec, x_dec)
        return x_dec, None
    else:
        zfs = []
        for i, zi in zip(list(range(Ndec)), zis):
            x_dec, zf = decimate(bdec, adec, x_dec, zi=zi)
            # zf can be reused to restart the filter
            zfs += [zf]
        return x_dec, zfs


def decimate_multiple_filtic(Ndec, bdec, adec):
    '''build a proper array of zero initial conditions to start the subsampler'''
    zfs = []
    for i in range(Ndec):
        l = max(len(bdec), len(adec)) - 1
        zfs += [numpy.zeros(l)]
    return zfs
