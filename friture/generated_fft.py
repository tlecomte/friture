# FFT filter data generated from filter_design.py
#
# This module loads precomputed FIR coefficients and FFT frequency responses
# for all bands-per-octave settings from a binary .npz file.

import numpy as np
from importlib.resources import files

_CACHE = None

def load_arrays():
    """Return a dict of precomputed FFT filter data for all bands-per-octave
    settings.  Results are cached after the first call."""
    global _CACHE
    if _CACHE is None:
        npz_path = files('friture.data').joinpath('generated_fft.npz')
        with npz_path.open('rb') as f:
            data = np.load(f)
            _CACHE = {k: data[k] for k in data.files}
    return _CACHE
