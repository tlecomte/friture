# -*- coding: utf-8 -*-
from numpy import pi, exp, arange, cos, sin, sqrt, zeros, ones, log, arange, set_printoptions
# the three following lines are a workaround for a bug with scipy and py2exe
# together. See http://www.pyinstaller.org/ticket/83 for reference.
from scipy.special import factorial
import scipy
scipy.factorial = factorial

# importing from scipy.signal.signaltools and scipy.signal.filter_design instead of scipy.signal
# decreases dramatically the number of modules imported
from scipy.signal.signaltools import lfilter
from scipy.signal.filter_design import ellip, butter, cheby1, iirdesign, freqz
from scipy.signal.fir_filter_design import firwin

# allow this script to properly import other friture modules
import sys
sys.path.insert(0, '.')
from friture.filter import (octave_frequencies, octave_filter_bank,
                            octave_filter_bank_decimation, NOCTAVE)

from friture.audiobackend import SAMPLING_RATE

# bank of filters for any other kind of frequency scale
# http://cobweb.ecn.purdue.edu/~malcolm/apple/tr35/PattersonsEar.pdf
# bandwidth of a cochlear channel as a function of center frequency

# Change the following parameters if you wish to use a different
# ERB scale.
EAR_Q = 9.26449  # Glasberg and Moore Parameters
MIN_BW = 24.7
ORDER = 1.


def frequencies(fs, num_channels, low_freq):
    channels = arange(0, num_channels)
    cf = -(EAR_Q * MIN_BW) + exp(channels * (-log(fs / 2 + EAR_Q * MIN_BW) +
                                             log(low_freq + EAR_Q * MIN_BW)) / num_channels) \
        * (fs / 2 + EAR_Q * MIN_BW)
    return cf


def MakeERBFilters(fs, num_channels, low_freq):
    # [forward, feedback] = MakeERBFilters(fs, num_channels) computes the
    # filter coefficients for a bank of Gammatone filters. These
    # filters were defined by Patterson and Holdworth for simulating
    # the cochlea. The results are returned as arrays of filter
    # coefficients. Each row of the filter arrays (forward and feedback)
    # can be passed to the MatLab "filter" function, or you can do all
    # the filtering at once with the ERBFilterBank() function.
    #
    # The filter bank contains "num_channels" channels that extend from
    # half the sampling rate (fs) to "low_freq".
    T = 1. / fs
    # All of the following expressions are derived in Apple TR #35, "An
    # Efficient Implementation of the Patterson-Holdsworth Cochlear
    # Filter Bank."
    cf = frequencies(fs, num_channels, low_freq)
    ERB = ((cf / EAR_Q) ** ORDER + MIN_BW ** ORDER) ** (1. / ORDER)
    B = 1.019 * 2 * pi * ERB
    gain = abs((-2 * exp(4 * 1j * cf * pi * T) * T +
                2 * exp(-(B * T) + 2 * 1j * cf * pi * T) * T *
                (cos(2 * cf * pi * T) - sqrt(3. - 2. ** (3. / 2.)) *
                 sin(2 * cf * pi * T))) *
               (-2 * exp(4 * 1j * cf * pi * T) * T +
                2 * exp(-(B * T) + 2 * 1j * cf * pi * T) * T *
                (cos(2 * cf * pi * T) + sqrt(3. - 2. ** (3. / 2.)) *
                 sin(2 * cf * pi * T))) *
               (-2 * exp(4 * 1j * cf * pi * T) * T +
                2 * exp(-(B * T) + 2 * 1j * cf * pi * T) * T *
                (cos(2 * cf * pi * T) -
                 sqrt(3. + 2. ** (3. / 2.)) * sin(2 * cf * pi * T))) *
               (-2 * exp(4 * 1j * cf * pi * T) * T + 2 * exp(-(B * T) + 2 * 1j * cf * pi * T) * T *
                (cos(2 * cf * pi * T) + sqrt(3. + 2. ** (3. / 2.)) * sin(2 * cf * pi * T))) /
               (-2 / exp(2 * B * T) - 2 * exp(4 * 1j * cf * pi * T) +
                2 * (1 + exp(4 * 1j * cf * pi * T)) / exp(B * T)) ** 4)

    feedback = zeros((len(cf), 9))
    forward = zeros((len(cf), 5))
    forward[:, 0] = T ** 4 / gain
    forward[:, 1] = -4 * T ** 4 * cos(2 * cf * pi * T) / exp(B * T) / gain
    forward[:, 2] = 6 * T ** 4 * cos(4 * cf * pi * T) / exp(2 * B * T) / gain
    forward[:, 3] = -4 * T ** 4 * cos(6 * cf * pi * T) / exp(3 * B * T) / gain
    forward[:, 4] = T ** 4 * cos(8 * cf * pi * T) / exp(4 * B * T) / gain
    feedback[:, 0] = ones(len(cf))
    feedback[:, 1] = -8 * cos(2 * cf * pi * T) / exp(B * T)
    feedback[:, 2] = 4 * (4 + 3 * cos(4 * cf * pi * T)) / exp(2 * B * T)
    feedback[:, 3] = -8 * (6 * cos(2 * cf * pi * T) + cos(6 * cf * pi * T)) / exp(3 * B * T)
    feedback[:, 4] = 2 * (18 + 16 * cos(4 * cf * pi * T) + cos(8 * cf * pi * T)) / exp(4 * B * T)
    feedback[:, 5] = -8 * (6 * cos(2 * cf * pi * T) + cos(6 * cf * pi * T)) / exp(5 * B * T)
    feedback[:, 6] = 4 * (4 + 3 * cos(4 * cf * pi * T)) / exp(6 * B * T)
    feedback[:, 7] = -8 * cos(2 * cf * pi * T) / exp(7 * B * T)
    feedback[:, 8] = exp(-8 * B * T)

    return [forward, feedback]


def octave_filters(total_band_count, bands_per_octave):
    # Bandpass Filter Generation
    pbrip = .5      # Pass band ripple
    sbrip = 50      # Stop band rejection
    # Filter order
    order = 2

    fi, f_low, f_high = octave_frequencies(total_band_count, bands_per_octave)

    fs = SAMPLING_RATE
    wi = fi / (fs / 2.)  # normalized frequencies
    w_low = f_low / (fs / 2.)
    w_high = f_high / (fs / 2.)
    w_high = (w_high < 1.) * w_high + (w_high >= 1.) * 1.

    B = []
    A = []

    # For each band
    for w, wl, wh in zip(wi, w_low, w_high):
        # normalized frequency vector
        freq = [wl, wh]

        # could be another IIR filter
        [b, a] = ellip(order, pbrip, sbrip, freq, btype='bandpass')

        B += [b]
        A += [a]

    return [B, A, fi, f_low, f_high]


def octave_filters_oneoctave(total_band_count, bands_per_octave):
    # Bandpass Filter Generation
    pbrip = .5      # Pass band ripple
    sbrip = 50      # Stop band rejection
    # Filter order
    order = 2

    fi, f_low, f_high = octave_frequencies(total_band_count, bands_per_octave)

    fi = fi[-bands_per_octave:]
    f_low = f_low[-bands_per_octave:]
    f_high = f_high[-bands_per_octave:]

    fs = SAMPLING_RATE
    wi = fi / (fs / 2.)  # normalized frequencies
    w_low = f_low / (fs / 2.)
    w_high = f_high / (fs / 2.)
    w_high = (w_high < 1.) * w_high + (w_high >= 1.) * 1.

    B = []
    A = []

    # For each band
    for w, wl, wh in zip(wi, w_low, w_high):
        # normalized frequency vector
        freq = [wl, wh]

        # could be another IIR filter
        [b, a] = ellip(order, pbrip, sbrip, freq, btype='bandpass')

        B += [b.tolist()]
        A += [a.tolist()]

    return [B, A, fi, f_low, f_high]


def generate_filters_params():
    import os
    import json

    params = {}

    # generate the low-pass filter for decimation
    Ndec = 3
    fc = 0.5
    # other possibilities
    # (bdec, adec) = ellip(Ndec, 0.05, 30, fc)
    # print(bdec)
    # (bdec, adec) = cheby1(Ndec, 0.05, fc)
    # (bdec, adec) = butter(Ndec, fc)
    (bdec, adec) = iirdesign(0.48, 0.50, 0.05, 70, analog=0, ftype='ellip', output='ba')
    # bdec = firwin(30, fc)
    # adec = [1.]

    # set_printoptions(precision=24)

    params['dec'] = [bdec.tolist(), adec.tolist()]

    # generate the octave filters
    for bands_per_octave in [1, 3, 6, 12, 24]:
        total_band_count = NOCTAVE * bands_per_octave
        [boct, aoct, fi, flow, fhigh] = octave_filters_oneoctave(total_band_count, bands_per_octave)
        params['%d' % bands_per_octave] = [boct, aoct, fi.tolist(), flow.tolist(), fhigh.tolist()]

    out = """\
# Filters parameters generated from filter_design.py

import json

JSON_PARAMS = \"\"\"
%s
\"\"\"

PARAMS = json.loads(JSON_PARAMS)
""" % json.dumps(params, indent=4, sort_keys=True)  # repr(params)

    path = os.path.dirname(__file__)
    fname = os.path.join(path, 'generated_filters.py')
    with open(fname, 'w') as output:
        output.write(out)

# main() is a test function


def main():
    from matplotlib.pyplot import semilogx, plot, show, xlim, ylim, figure, legend, subplot, bar
    from numpy.fft import fft, fftfreq, fftshift, ifft
    from numpy import log10, linspace, interp, angle, array, concatenate

    N = 2048 * 2 * 2
    fs = float(SAMPLING_RATE)
    channel_count = 20
    low_freq = 20.

    impulse = zeros(N)
    impulse[N / 2] = 1
    f = 1000.
    # impulse = sin(2*pi*f*arange(0, N/fs, 1./fs))

    # [ERBforward, ERBfeedback] = MakeERBFilters(fs, channel_count, low_freq)
    # y = ERBFilterBank(ERBforward, ERBfeedback, impulse)

    bands_per_octave = 3
    total_band_count = NOCTAVE * bands_per_octave

    [B, A, fi, fl, fh] = octave_filters(total_band_count, bands_per_octave)
    y, zfs = octave_filter_bank(B, A, impulse)
    # print "Filter lengths without decimation"
    # for b, a in zip(B, A):
    #       print len(b), len(a)

    response = 20. * log10(abs(fft(y)))
    freqScale = fftfreq(N, 1. / fs)

    figure()
    subplot(211)

    for i in range(0, response.shape[0]):
        semilogx(freqScale[0:int(N / 2)], response[i, 0:int(N / 2)])

    xlim(fs / 2000, fs)
    ylim(-70, 10)

    subplot(212)
    m = 0
    for f in fi:
        p = 10. * log10((y[m] ** 2).mean())
        m += 1
        semilogx(f, p, 'ko')

    Ndec = 3
    fc = 0.5
    # other possibilities
    # (bdec, adec) = ellip(Ndec, 0.05, 30, fc)
    # print bdec
    # (bdec, adec) = cheby1(Ndec, 0.05, fc)
    # (bdec, adec) = butter(Ndec, fc)
    (bdec, adec) = iirdesign(0.48, 0.50, 0.05, 70, analog=0, ftype='ellip', output='ba')
    # bdec = firwin(30, fc)
    # adec = [1.]

    figure()
    subplot(211)

    response = 20. * log10(abs(fft(impulse)))
    plot(fftshift(freqScale), fftshift(response), label="impulse")

    y = lfilter(bdec, adec, impulse)
    response = 20. * log10(abs(fft(y)))
    plot(fftshift(freqScale), fftshift(response), label="lowpass")

    ydec = y[::2].repeat(2)
    response = 20. * log10(abs(fft(ydec)))
    plot(fftshift(freqScale), fftshift(response), label="lowpass + dec2 + repeat2")

    ydec2 = interp(list(range(0, len(y))), list(range(0, len(y), 2)), y[::2])
    response = 20. * log10(abs(fft(ydec2)))
    plot(fftshift(freqScale), fftshift(response), label="lowpass + dec2 + interp2")

    ydec3 = y[::2]
    response = 20. * log10(abs(fft(ydec3)))
    freqScale2 = fftfreq(int(N / 2), 2. / fs)
    plot(freqScale2, fftshift(response), label="lowpass + dec2")

    legend(loc="lower left")

    subplot(212)
    plot(list(range(0, len(impulse))), impulse, label="impulse")
    plot(list(range(0, len(impulse))), y, label="lowpass")
    plot(list(range(0, len(impulse))), ydec, label="lowpass + dec2 + repeat2")
    plot(list(range(0, len(impulse))), ydec2, label="lowpass + dec2 + interp2")
    plot(list(range(0, len(impulse), 2)), ydec3, label="lowpass + dec2")
    legend()

    [boct, aoct, fi, flow, fhigh] = octave_filters_oneoctave(total_band_count, bands_per_octave)
    y, dec, zfs = octave_filter_bank_decimation(bdec, adec, boct, aoct, impulse)
    # print "Filter lengths with decimation"
    # print len(bdec), len(adec)
    # for b, a in zip(boct, aoct):
    #       print len(b), len(a)

    figure()
    subplot(211)

    for yone, d in zip(y, dec):
        response = 20. * log10(abs(fft(yone)) * d)
        freqScale = fftfreq(int(N / d), 1. / (fs / d))
        semilogx(freqScale[0:int(N / (2 * d))], response[0:int(N / (2 * d))])

    xlim(fs / 2000, fs)
    ylim(-70, 10)

    subplot(212)
    m = 0
    for i in range(0, NOCTAVE):
        for f in fi:
            p = 10. * log10((y[m] ** 2).mean())
            semilogx(f / dec[m], p, 'ko')
            m += 1

    [boct, aoct, fi, flow, fhigh] = octave_filters_oneoctave(total_band_count, bands_per_octave)
    y1, dec, zfs = octave_filter_bank_decimation(bdec, adec, boct, aoct, impulse[0:int(N / 2)])
    y2, dec, zfs = octave_filter_bank_decimation(bdec, adec, boct, aoct, impulse[int(N / 2):], zis=zfs)

    y = []
    for y1one, y2one in zip(y1, y2):
        y += [concatenate((y1one, y2one))]

    figure()
    subplot(211)

    for yone, d in zip(y, dec):
        response = 20. * log10(abs(fft(yone)) * d)
        freqScale = fftfreq(int(N / d), 1. / (fs / d))
        semilogx(freqScale[0:int(N / (2 * d))], response[0:int(N / (2 * d))])

    xlim(fs / 2000, fs)
    ylim(-70, 10)

    subplot(212)
    m = 0
    for i in range(0, NOCTAVE):
        for f in fi:
            p = 10. * log10((y[m] ** 2).mean())
            semilogx(f / dec[m], p, 'ko')
            m += 1

    generate_filters_params()

    show()

if __name__ == "__main__":
    main()
