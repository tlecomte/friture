# -*- coding: utf-8 -*-
from numpy import arange, sqrt, zeros, array
from friture_extensions.lfilter import pyx_lfilter_float64_1D
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
#     where
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
        filt, zf = pyx_lfilter_float64_1D(forward[i], feedback[i], x, zis[i])
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
            filt, zf = pyx_lfilter_float64_1D(forward[i], feedback[i], x_dec, zis[m])
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
