# FFT filter data generated from filter_design.py
#
# This module loads precomputed FIR coefficients and FFT frequency responses
# for all bands-per-octave settings from a binary .npz file.

import os
import sys

import numpy as np

_CACHE = None

def _npz_path():
    # In a frozen (PyInstaller) bundle the data shipped by friture.spec lives
    # next to the application binary; in a normal checkout it sits in the
    # source tree under friture/data/.
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(os.path.abspath(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'data', 'generated_fft.npz')

def load_arrays():
    """Return a dict of precomputed FFT filter data for all bands-per-octave
    settings.  Results are cached after the first call."""
    global _CACHE
    if _CACHE is None:
        with open(_npz_path(), 'rb') as f:
            data = np.load(f)
            _CACHE = {k: data[k] for k in data.files}
    return _CACHE
