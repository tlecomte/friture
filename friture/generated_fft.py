# FFT filter data generated from filter_design.py
#
# This module loads precomputed FIR coefficients and FFT frequency responses
# for all bands-per-octave settings from a binary .npz file.

import os
import sys

import numpy as np

_CACHE = None

def _data_path(name):
    # PyInstaller onedir exposes the bundle's data directory (which holds every
    # collected data file, including those shipped via friture.spec's `datas`)
    # as sys._MEIPASS. In a source checkout we resolve relative to this file so
    # `import friture` from anywhere in the tree still finds the data.
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'data', name)

def load_arrays():
    """Return a dict of precomputed FFT filter data for all bands-per-octave
    settings.  Results are cached after the first call."""
    global _CACHE
    if _CACHE is None:
        with open(_data_path('generated_fft.npz'), 'rb') as f:
            data = np.load(f)
            _CACHE = {k: data[k] for k in data.files}
    return _CACHE
