# -*- coding: utf-8 -*-
"""
Pure-Python implementations of IIR filtering and IIR-to-FIR conversion.

* :func:`lfilter_float64_1D` implements a single direct-form II
  transposed IIR filter using Python lists for fast scalar arithmetic.
  It is used by the legacy pure-IIR octave filter bank and the
  :func:`decimate` helper.

* :func:`iir_to_minphase_fir` converts an IIR filter to a minimum-phase
  FIR approximation via cepstral processing.  The IIR impulse response
  is obtained in the frequency domain (z-transform on the unit circle)
  rather than time-domain filtering, making it ~200x faster.  The
  resulting FIR has the same magnitude response and a compactly decaying
  impulse response, enabling fast FFT-based overlap-add convolution.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt


def iir_to_minphase_fir(
    b: npt.NDArray[np.float64],
    a: npt.NDArray[np.float64],
    fir_length: int,
    fft_size: int = 8192,
) -> npt.NDArray[np.float64]:
    """Convert an IIR filter to a minimum-phase FIR filter via cepstral processing.

    The resulting FIR filter has the **same magnitude response** as the
    original IIR filter but with all zeros inside the unit circle, producing
    a causal, compactly-decaying impulse response.  This makes it suitable
    for exact FFT-based overlap-add convolution (the overlap state is simply
    the FIR tail, with no recursive error propagation).

    Parameters
    ----------
    b : 1D array
        Numerator coefficients of the IIR filter.
    a : 1D array
        Denominator coefficients of the IIR filter (a[0] should be 1).
    fir_length : int
        Length of the resulting FIR filter.
    fft_size : int, optional
        FFT size for the cepstral computation (default 8192).  Must be
        large enough to capture the full IIR impulse response.

    Returns
    -------
    h_fir : 1D array of length *fir_length*
        Minimum-phase FIR filter coefficients.
    """
    N = fft_size

    # Compute the IIR frequency response via the z-transform.
    # Evaluate B(z) and A(z) on the unit circle.  This is far faster than
    # computing the time-domain impulse response with lfilter_float64_1D
    # (which loops in Python over every sample).
    w = np.exp(-1j * 2.0 * np.pi * np.arange(N) / N)   # N roots of unity
    # polyval expects coefficients in descending power order; our b/a are
    # already in ascending z^-1 order, so reverse for polyval.
    B = np.polyval(b[::-1], w)
    A = np.polyval(a[::-1], w)
    H = B / A

    # Cepstral minimum-phase conversion
    log_mag = np.log(np.abs(H) + 1e-30)
    c = np.fft.ifft(log_mag, N).real

    c_min = np.zeros(N)
    c_min[0] = c[0]
    c_min[1:N // 2] = 2 * c[1:N // 2]
    c_min[N // 2] = c[N // 2]

    C_min = np.fft.fft(c_min, N)
    H_min = np.exp(C_min)

    h_min = np.fft.ifft(H_min, N).real

    return h_min[:fir_length]


def lfilter_float64_1D(
    b: npt.NDArray[np.float64],
    a: npt.NDArray[np.float64],
    x: npt.NDArray[np.float64],
    zi: npt.NDArray[np.float64],
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """
    Filter data along one dimension with an IIR or FIR filter.

    Direct form II transposed implementation of the standard difference equation::

        a[0]*y[n] = b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb]
                                - a[1]*y[n-1] - ... - a[na]*y[n-na]

    Parameters
    ----------
    b : 1D array
        Numerator coefficient vector.
    a : 1D array
        Denominator coefficient vector.  ``a[0]`` should be 1.
    x : 1D array
        Input signal.
    zi : 1D array
        Initial filter delay state, length ``max(len(a), len(b)) - 1``.

    Returns
    -------
    y : 1D array
        Filtered output.
    zf : 1D array
        Final filter delay state (can be reused for continuous filtering).
    """
    assert b.shape[0] == a.shape[0], "a and b must be of the same shape"
    assert zi.shape[0] == b.shape[0] - 1

    # Convert to Python lists for fast scalar access
    b_list = b.tolist()
    a_list = a.tolist()
    x_list = x.tolist()
    z_list = zi.tolist()

    len_x = len(x_list)
    len_b = len(b_list)

    y_list = [0.0] * len_x

    if len_b > 1:
        for k in range(len_x):
            yk = z_list[0] + b_list[0] * x_list[k]
            y_list[k] = yk

            for n in range(len_b - 2):
                z_list[n] = z_list[n + 1] + x_list[k] * b_list[n + 1] - yk * a_list[n + 1]

            z_list[len_b - 2] = x_list[k] * b_list[len_b - 1] - yk * a_list[len_b - 1]
    else:
        for k in range(len_x):
            y_list[k] = x_list[k] * b_list[0]

    y = np.array(y_list, dtype=np.float64)
    z = np.array(z_list, dtype=np.float64)

    return y, z
