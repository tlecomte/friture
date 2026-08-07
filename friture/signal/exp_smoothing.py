# -*- coding: utf-8 -*-

from __future__ import annotations

import numpy as np
import numpy.typing as npt

dtype = np.float64


def exp_smoothed_value(
    kernel: npt.NDArray[np.float64],
    alpha: float,
    data: npt.NDArray[np.float64],
    previous: float,
) -> float:
    """
    Compute exponential smoothing of a 1D data array using a precomputed kernel.

    This is equivalent to applying the IIR filter:
        y_i = alpha*x_i + (1-alpha)*y_{i-1}
    but computed efficiently via a convolution with a precomputed kernel.

    Parameters:
    -----------
    kernel : 1D array
        The pre-computed convolution kernel for the exponential smoothing.
    alpha : float
        The exponential smoothing factor, between 0 and 1.
    data : 1D array
        The input data to filter.
    previous : float
        The previous filtered value.

    Returns:
    --------
    float
        The filtered value.
    """
    N = data.shape[0]
    Nk = kernel.shape[0]

    if N > Nk:
        N = Nk
        a = 0.0
    else:
        a = (1.0 - alpha) ** N

    if N == 0:
        return previous

    conv = np.dot(kernel[Nk - N:Nk], data[:N])

    value = alpha * conv + previous * a

    return float(value)


def exp_smoothed_value_2d(
    kernel: npt.NDArray[np.float64],
    alpha: float,
    data: npt.NDArray[np.float64],
    previous: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """
    Compute exponential filtering of 2D data with given kernel and alpha.
    The filter is applied on the 2nd axis (axis=1), independently for each row (axis=0).

    This is equivalent to applying the following IIR filter on each row of data:
    y_i = alpha*x_i + (1-alpha)*y_{i-1}
    where x_i is the input data, y_i the filtered data, and y_{i-1} the previous filtered value.

    By using a precomputed kernel, this function is optimized to process a large number of samples at once.

    Parameters:
    -----------
    kernel : 1D array
        The pre-computed convolution kernel for the exponential smoothing.
    alpha : float
        The exponential smoothing factor, between 0 and 1.
    data : 2D array
        The input data to filter, shape (Nf, Nt).
    previous : 1D array
        The previous filtered value, shape (Nf,).

    Returns:
    --------
    1D array
        The filtered value, shape (Nf,).
    """
    Nf, Nt = data.shape
    Nk = kernel.shape[0]

    if Nt > Nk:
        Nt = Nk
        a = 0.0
    else:
        a = (1.0 - alpha) ** Nt

    if Nt == 0:
        return np.array(previous, copy=True)

    conv = data[:, :Nt] @ kernel[Nk - Nt:Nk]

    value = alpha * conv + previous * a

    return value
