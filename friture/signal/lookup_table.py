# -*- coding: utf-8 -*-

from __future__ import annotations

import numpy as np
import numpy.typing as npt


def color_from_float(
    lut: npt.NDArray[np.uint32],
    values: npt.NDArray[np.float64],
) -> npt.NDArray[np.uint32]:
    """
    Convert float values [0, 1] to uint32 colors by looking up a LUT.

    Parameters:
    -----------
    lut : 1D array of uint32
        Lookup table of colors, indexed by int(value * 255).
    values : 1D array of float64
        Input float values in [0, 1].

    Returns:
    --------
    1D array of uint32
        Color values.
    """
    indices = np.clip((values * 255).astype(np.intp), 0, lut.shape[0] - 1)
    return lut[indices]


def color_from_float_2D(
    lut: npt.NDArray[np.uint32],
    values: npt.NDArray[np.float64],
) -> npt.NDArray[np.uint32]:
    """
    Convert 2D float values [0, 1] to 2D uint32 colors by looking up a LUT.

    Parameters:
    -----------
    lut : 1D array of uint32
        Lookup table of colors, indexed by int(value * 255).
    values : 2D array of float64
        Input float values in [0, 1].

    Returns:
    --------
    2D array of uint32
        Color values.
    """
    indices = np.clip((values * 255).astype(np.intp), 0, lut.shape[0] - 1)
    return lut[indices]


def rgb_from_float_2D(
    lut: npt.NDArray[np.uint32],
    values: npt.NDArray[np.float64],
) -> npt.NDArray[np.uint32]:
    """
    Convert 2D float values [0, 1] to 3D uint32 RGB array by looking up a LUT.

    Parameters:
    -----------
    lut : 2D array of uint32, shape (256, 3)
        Lookup table of RGB color components.
    values : 2D array of float64
        Input float values in [0, 1].

    Returns:
    --------
    3D array of uint32, shape (M, N, 3)
        RGB color values.
    """
    indices = np.clip((values * 255).astype(np.intp), 0, lut.shape[0] - 1)
    return lut[indices, :]
