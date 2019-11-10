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
#
# ------------------------
#
# This particular file contains just the resample function taken out of Scipy (to avoid having to include all of Scipy).
# The original Scipy license follows:
#
# Copyright © 2001, 2002 Enthought, Inc.
# All rights reserved.
#
# Copyright © 2003-2013 SciPy Developers.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#     Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#     Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer
#     in the documentation and/or other materials provided with the distribution.
#     Neither the name of Enthought nor the names of the SciPy Developers may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

from numpy.fft import fft, ifft, ifftshift, fftfreq
from numpy import (arange, asarray, ndarray, zeros)
import numpy as np


def resample(x, num, t=None, axis=0, window=None):
    """
    Resample `x` to `num` samples using Fourier method along the given axis.

    The resampled signal starts at the same value as `x` but is sampled
    with a spacing of ``len(x) / num * (spacing of x)``.  Because a
    Fourier method is used, the signal is assumed to be periodic.

    Parameters
    ----------
    x : array_like
        The data to be resampled.
    num : int
        The number of samples in the resampled signal.
    t : array_like, optional
        If `t` is given, it is assumed to be the sample positions
        associated with the signal data in `x`.
    axis : int, optional
        The axis of `x` that is resampled.  Default is 0.
    window : array_like, callable, string, float, or tuple, optional
        Specifies the window applied to the signal in the Fourier
        domain.  See below for details.

    Returns
    -------
    resampled_x or (resampled_x, resampled_t)
        Either the resampled array, or, if `t` was given, a tuple
        containing the resampled array and the corresponding resampled
        positions.

    Notes
    -----
    The argument `window` controls a Fourier-domain window that tapers
    the Fourier spectrum before zero-padding to alleviate ringing in
    the resampled values for sampled signals you didn't intend to be
    interpreted as band-limited.

    If `window` is a function, then it is called with a vector of inputs
    indicating the frequency bins (i.e. fftfreq(x.shape[axis]) ).

    If `window` is an array of the same length as `x.shape[axis]` it is
    assumed to be the window to be applied directly in the Fourier
    domain (with dc and low-frequency first).

    For any other type of `window`, the function `scipy.signal.get_window`
    is called to generate the window.

    The first sample of the returned vector is the same as the first
    sample of the input vector.  The spacing between samples is changed
    from dx to:

        dx * len(x) / num

    If `t` is not None, then it represents the old sample positions,
    and the new sample positions will be returned as well as the new
    samples.

    """
    x = asarray(x)
    X = fft(x, axis=axis)
    Nx = x.shape[axis]
    if window is not None:
        if callable(window):
            W = window(fftfreq(Nx))
        elif isinstance(window, ndarray) and window.shape == (Nx,):
            W = window
        else:
            W = ifftshift(get_window(window, Nx))
        newshape = [1] * x.ndim
        newshape[axis] = len(W)
        W.shape = newshape
        X = X * W
    sl = [slice(None)] * len(x.shape)
    newshape = list(x.shape)
    newshape[axis] = num
    N = int(np.minimum(num, Nx))
    Y = zeros(newshape, 'D')
    sl[axis] = slice(0, (N + 1) // 2)
    Y[tuple(sl)] = X[tuple(sl)]
    sl[axis] = slice(-(N - 1) // 2, None)
    Y[tuple(sl)] = X[tuple(sl)]
    y = ifft(Y, axis=axis) * (float(num) / float(Nx))

    if x.dtype.char not in ['F', 'D']:
        y = y.real

    if t is None:
        return y
    else:
        new_t = arange(0, num) * (t[1] - t[0]) * Nx / float(num) + t[0]
        return y, new_t
