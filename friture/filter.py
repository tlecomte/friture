# -*- coding: utf-8 -*-
from numpy import arange, sqrt, zeros, array
import numpy as np
from friture.signal.lfilter import lfilter_float64_1D
from .signal.decimate import decimate

NOCTAVE = 9


def ERBFilterBank(forward, feedback, x):
    # y=ERBFilterBank(forward, feedback, x)
    # This function filters the waveform x with the array of filters
    # specified by the forward and feedback parameters. Each row
    # of the forward and feedback parameters are the parameters
    # to the Matlab builtin function "filter".
    rows = feedback.shape[0]
    y = zeros((rows, len(x)))
    for i in range(0, rows):
        y[i, :] = lfilter(forward[i, :], feedback[i, :], x)
    return y

# Nominal frequencies: 31.5 40 50 63 80 100 125 160 200 250 315 400 500 630 800 1000 1250
# 1600 2000 Hz, etc.
#
# http://zone.ni.com/devzone/cda/tut/p/id/2975
# According to the IEC 1260:1995 and the ANSI S1.11:2004 standards, the midband (or center) frequency of the bandpass filter
# is defined by the following equations:
#
#     fi = 1000 * 2ib for 1/N octave filters when N is odd
#
#     fi = 1000 * 2(i+1)b/2 for 1/N octave filters when N is even
#
#     where:
#     fi is the center frequency of the ith band-pass filter expressed in hertz.
#     i is an integer when i = 0, f0 = 1 kHz, which is the reference frequency for the audio range.
#     b is the bandwidth designator and equals 1 for octave, 1/3 for 1/3 octave, 1/6 for 1/6 octave, 1/12 for 1/12 octave, and 1/24 for 1/24 octave.


def octave_frequencies(total_bands_count, bands_per_octave):
    f0 = 1000.  # audio reference frequency is 1 kHz

    b = 1. / bands_per_octave

    imax = total_bands_count // 2
    if total_bands_count % 2 == 0:
        i = arange(-imax, imax)
    else:
        i = arange(-imax, imax + 1)

    fi = f0 * 2 ** (i * b)
    f_low = fi * sqrt(2 ** (-b))
    f_high = fi * sqrt(2 ** b)

    return fi, f_low, f_high


def octave_filter_bank(forward, feedback, x, zis=None):
    # This function filters the waveform x with the array of filters
    # specified by the forward and feedback parameters. Each row
    # of the forward and feedback parameters are the parameters
    # to the Matlab builtin function "filter".
    filter_count = len(forward)
    y = zeros((filter_count, len(x)))

    zfs = []
    y = []

    if zis is None:
        zis = []
        for i in range(0, filter_count):
            zis += [zeros(max(len(forward[i]), len(feedback[i])) - 1)]

    for i in range(0, filter_count):
        filt, zf = lfilter_float64_1D(forward[i], feedback[i], x, zis[i])
        # zf can be reused to restart the filter
        zfs += [zf]
        y += [filt]

    return y, zfs

# Note: we may have one filter in excess here : the low-pass filter for decimation
# does approximately the same thing as the low-pass component of the highest band-pass
# filter for the octave


def octave_filter_bank_decimation(blow, alow, forward, feedback, x, zis):
    # This function filters the waveform x with the array of filters
    # specified by the forward and feedback parameters. Each row
    # of the forward and feedback parameters are the parameters
    # to the Matlab builtin function "filter".
    bands_per_octave = len(forward)
    filter_count = NOCTAVE * bands_per_octave

    y = [0.] * filter_count
    dec = [0.] * filter_count

    x_dec = x

    zfs = []

    m = 0
    k = filter_count - 1

    for j in range(0, NOCTAVE):
        for i in range(0, bands_per_octave)[::-1]:
            filt, zf = lfilter_float64_1D(forward[i], feedback[i], x_dec, zis[m])
            m += 1
            # zf can be reused to restart the filter
            zfs += [zf]
            y[k] = filt
            dec[k] = 2 ** j
            k -= 1
        x_dec, zf = decimate(blow, alow, x_dec, zis[m])
        m += 1
        # zf can be reused to restart the filter
        zfs += [zf]

    return y, dec, zfs


def octave_filter_bank_decimation_filtic(blow, alow, forward, feedback):
    '''build a proper array of zero initial conditions to start the filters.'''
    bands_per_octave = len(forward)
    zfs = []

    for j in range(0, NOCTAVE):
        for i in range(0, bands_per_octave)[::-1]:
            l = max(len(forward[i]), len(feedback[i])) - 1
            zfs += [zeros(l)]
        l = max(len(blow), len(alow)) - 1
        zfs += [zeros(l)]

    return zfs


def octave_filter_bank_decimation_fft(
    boct,
    fft_H_oct, fft_H_dec, fft_sizes,
    fir_length,
    x,
    overlaps_oct, overlaps_dec,
):
    """All-FFT octave filter bank with decimation.

    Uses FFT-based overlap-add with minimum-phase FIR approximations for
    every stage.  When the block size is smaller than fir_length-1, the
    overlap tail from one block extends beyond the next block's output;
    this is handled by accumulating pending overlap samples across blocks
    via element-wise addition (not concatenation), keeping the pending
    buffer at a fixed fir_length-1 entries.

    Parameters
    ----------
    boct : list of 1D arrays
        Original IIR octave filter coefficients (used only to determine
        bands_per_octave via ``len(boct)``).
    fft_H_oct : list of 2D arrays
        Precomputed rfft of each octave FIR, one per FFT stage.
        Shape per entry: (bands_per_octave, fft_size//2+1).
    fft_H_dec : list of 1D arrays
        Precomputed rfft of each decimation FIR, one per FFT stage.
    fft_sizes : list of int
        FFT size for each FFT stage.
    fir_length : int
        Length of the minphase FIR filters.
    x : 1D array
        Input signal.
    overlaps_oct : list of 2D arrays
        Overlap buffers for octave filters at each stage.
        Each has shape (bands_per_octave, fir_length-1).
    overlaps_dec : list of 1D arrays
        Overlap buffers for decimation filter at each stage.
        Each has length fir_length-1.

    Returns
    -------
    y : list of 1D arrays
        Filtered outputs, one per band (total NOCTAVE * bands_per_octave).
    dec : list of int
        Decimation factor for each band.
    overlaps_oct : updated overlap buffers for FFT stages.
    overlaps_dec : updated overlap buffers for FFT stages.
    """
    bands_per_octave = len(boct)
    filter_count = NOCTAVE * bands_per_octave

    y = [None] * filter_count
    dec = [0] * filter_count

    k = filter_count - 1       # output index (filled high → low)
    x_dec = x
    L = fir_length
    Lm1 = L - 1

    for j in range(NOCTAVE):
        N_s = len(x_dec)
        dec_val = 2 ** j

        # --- FFT overlap-add stage ---
        fft_size = fft_sizes[j]
        n_freq = fft_size // 2 + 1
        H_oct = fft_H_oct[j]
        H_dec = fft_H_dec[j]

        # Shared input FFT
        X = np.fft.rfft(x_dec, fft_size)

        # Octave bandpass filters (batched multiply + irfft)
        Y_oct = X[np.newaxis, :] * H_oct          # (bpo, n_freq)
        y_oct_full = np.fft.irfft(Y_oct, fft_size, axis=1)  # (bpo, fft_size)

        # Add pending overlap from previous block (element-wise)
        pending = overlaps_oct[j]
        add_len = min(pending.shape[1], N_s)
        if add_len > 0:
            y_oct_full[:, :add_len] += pending[:, :add_len]

        # Decimation filter (FFT) — uses the same X
        Y_dec = X * H_dec
        y_dec_full = np.fft.irfft(Y_dec, fft_size)
        pending_d = overlaps_dec[j]
        add_len_d = min(len(pending_d), N_s)
        if add_len_d > 0:
            y_dec_full[:add_len_d] += pending_d[:add_len_d]

        # Assign outputs in reverse order (filter bpo-1 → position k, ..., filter 0 → position k-bpo+1)
        for i in range(bands_per_octave)[::-1]:
            y[k] = y_oct_full[i, :N_s]
            dec[k] = dec_val
            k -= 1

        x_dec = y_dec_full[:N_s:2]

        # Update pending buffers via element-wise addition of overlapping tails.
        new_tail = y_oct_full[:, N_s:N_s + Lm1]
        old_remaining = pending[:, add_len:]
        if old_remaining.shape[1] > 0:
            new_tail[:, :old_remaining.shape[1]] += old_remaining
        overlaps_oct[j] = new_tail.copy()

        new_tail_d = y_dec_full[N_s:N_s + Lm1]
        old_remaining_d = pending_d[add_len_d:]
        if len(old_remaining_d) > 0:
            new_tail_d[:len(old_remaining_d)] += old_remaining_d
        overlaps_dec[j] = new_tail_d.copy()

    return y, dec, overlaps_oct, overlaps_dec


def _next_composite_size(n):
    """Find the smallest FFT size >= n that numpy can compute efficiently.

    numpy's pocketfft dispatches to Bluestein or chirp-z for prime sizes
    (very slow) and mixed-radix for composites.  We try powers of two
    first; if those are much larger than *n*, we also try nearby products
    of 2, 3, and 5 (e.g. 768 = 3×256, 640 = 5×128) which pocketfft handles
    well at a smaller size.
    """
    # Fast path: round up to next power of two
    pow2 = 1
    while pow2 < n:
        pow2 *= 2

    # Try composite sizes (products of 2, 3, 5) below pow2
    best = pow2
    for size in range(n, pow2):
        s = size
        for p in (2, 3, 5):
            while s % p == 0:
                s //= p
        if s == 1:  # size is 5-smooth
            best = size
            break
    return best

