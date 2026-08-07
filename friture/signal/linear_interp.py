# -*- coding: utf-8 -*-

from __future__ import annotations

import numpy as np
import numpy.typing as npt

dtype = np.float64


def linear_interp_2D(
    resampled_buffer: npt.NDArray[np.float64],
    data: npt.NDArray[np.float64],
    old_data: npt.NDArray[np.float64],
    orig_index: float,
    resampled_index: float,
    resampling_ratio: float,
    n: int,
) -> float:
    """
    Apply linear interpolation along the time axis to resample a 2D buffer.

    For each of n output samples, linearly interpolate between corresponding
    elements of *data* and *old_data* based on the resampling ratio.

    Parameters:
    -----------
    resampled_buffer : 2D array
        Output buffer of shape (N, >=n). Filled in-place.
    data : 1D array
        Current input data.
    old_data : 1D array
        Previous input data.
    orig_index : float
        Original index (current position in the input stream).
    resampled_index : float
        Current position in the resampled stream.
    resampling_ratio : float
        Ratio of interpolation to decimation factors.
    n : int
        Number of output samples to produce.

    Returns:
    --------
    float
        The updated resampled index.
    """
    # Compute the resampled indices for all n samples at once
    # resampled_index starts at its current value and is incremented by
    # resampling_ratio for each sample (matching the original algorithm).
    new_indices = resampled_index + resampling_ratio * np.arange(1, n + 1, dtype=dtype)
    a_values = orig_index - new_indices

    # resampled_buffer[j, i] = (1 - a) * data[j] + a * old_data[j]
    # Using broadcasting: a_values shape (n,), data/old_data shape (N,)
    # Result shape: (N, n)
    resampled_buffer[:, :n] = (
        data[:, None] * (1.0 - a_values)[None, :]
        + old_data[:, None] * a_values[None, :]
    )

    return float(new_indices[-1])
