#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

from numpy import argmax
import numpy
import numpy as np
from numpy.fft import rfft, irfft, fft, ifft
from friture.filter import decimate
from friture import generated_filters
from friture.ringbuffer import RingBuffer
from friture.audiobackend import SAMPLING_RATE
from friture.delay_estimator import subsampler, subsampler_filtic, DEFAULT_DELAYRANGE, generalized_cross_correlation
from scipy.io import wavfile
import matplotlib.pyplot as plt

def main():
    Ns = 44100*20 #44100*60*3 #3000000

    print "Loading data"

    if True:
        # load data
        #fname = 'sandbox/test_cpea_20120602_part3.wav' # delay = 45.2 ms = 1993 samples (from Friture cross-correlation measurements)
        #fname = 'sandbox/gary_moore_separate_chambre.wav'
        #fname = 'sandbox/gary_moore_loner_chambre.wav'
        fname = 'sandbox/test_cpea_20120602.wav'
        #data, fs, enc = wavread(fname)
        fs, data = wavfile.read(fname)

        print data.shape, data.dtype
        data = data.astype(np.float64) # convert from integer to floats for computations

        ht = None

        #data = data[:Ns,:]
        data /= 2**16
        #data = data[::-1,:]

        # original signal
        x = data[:Ns,0]
        
        # measured signal
        m = data[:Ns,1]

    print "Data loaded"

    # We will decimate several times
    # no decimation => 1/fs = 23 µs resolution
    # 1 ms resolution => fs = 1000 Hz is enough => can divide the sampling rate by 44 !
    # if I decimate 2 times (2**2 = 4 => 0.092 ms (3 cm) resolution)!
    # if I decimate 3 times (2**3 = 8 => 0.184 ms (6 cm) resolution)!
    # if I decimate 4 times (2**4 = 16 => 0.368 ms (12 cm) resolution)!
    # if I decimate 5 times (2**5 = 32 => 0.7 ms (24 cm) resolution)!
    # (actually, I could fit a gaussian on the cross-correlation peak to get
    # higher resolution even at low sample rates)
    Ndec = 2
    subsampled_sampling_rate = SAMPLING_RATE/2**(Ndec)
    [bdec, adec] = generated_filters.params['dec']
    zfs0 = subsampler_filtic(Ndec, bdec, adec)
    zfs1 = subsampler_filtic(Ndec, bdec, adec)
    
    delayrange_s = DEFAULT_DELAYRANGE # confidence range

    # separate the channels
    x0 = x
    x1 = m
    #subsample them
    print "subsampling x0"
    x0_dec, zfs0 = subsampler(Ndec, bdec, adec, x0, zfs0)
    print "subsampling x1"
    x1_dec, zfs1 = subsampler(Ndec, bdec, adec, x1, zfs1)

    time = 2*delayrange_s
    length = time*subsampled_sampling_rate
    Ns_dec = Ns/2**(Ndec)
    overlap = 0.5
    Nb = int((1./overlap)*(Ns_dec/length - 1))

    old_Xcorr = np.zeros((length), np.complex128)

    print "time =", time
    print "length =", length
    print "Ns_dec = ", Ns_dec
    print "Nb =", Nb

    # Hann window to mitigate non-periodicity effects
    window = numpy.hanning(length)

    #l2 = length/2 + 1
    # Hann window to mitigate non-periodicity effects
    #window2 = numpy.hanning(l2)

    #f1 = plt.figure()
    #plt1 = f1.add_subplot(1,1,1)
    #f2 = plt.figure()
    #plt2 = f2.add_subplot(1,1,1)

    for i in range(Nb):
        print i
        # retrieve last one-second of data

        d0 = x0_dec[i*length*overlap:i*length*overlap + length]
        d1 = x1_dec[i*length*overlap:i*length*overlap + length]

        std0 = numpy.std(d0)
        std1 = numpy.std(d1)
        if d0.size>0 and std0>0. and std1>0.:
            Xcorr = generalized_cross_correlation(d0, d1)

            #plt1.plot(Xcorr)
            #plt.figure()
            #plt.plot(Xcorr)
            #plt.draw()

            if old_Xcorr != None and old_Xcorr.shape == Xcorr.shape:
                # smoothing
                alpha = 0.15
                Xcorr = alpha*Xcorr + (1. - alpha)*old_Xcorr
            
            #plt2.plot(Xcorr)
            #plt.draw()

            absXcorr = numpy.abs(Xcorr)
            ind = argmax(absXcorr)

            #h2_ = fft(absXcorr**2)
            #N = len(h2_)
            #h2_[N/50:-N/50] = 0.
            #h2 = ifft(h2_)
            #ind = argmax(h2)

            #plt.figure()
            #plt.plot(Xcorr)
            #plt.plot(absXcorr)
            #plt.draw()

            # normalize
            #Xcorr_max_norm = Xcorr_unweighted[ind]/(d0.size*std0*std1)
            Xcorr_extremum = Xcorr[ind]
            Xcorr_max_norm = abs(Xcorr[ind])/(3*numpy.std(Xcorr))
            delay_ms = 1e3*float(ind)/subsampled_sampling_rate
        
            # store for smoothing
            old_Xcorr = Xcorr
        else:
            delay_ms = 0.
            Xcorr_max_norm = 0.
            Xcorr_extremum = 0.

        # debug wrong phase detection
        #if Xcorr[i] < 0.:
        #    numpy.save("Xcorr.npy", Xcorr)

        c = 340. # speed of sound, in meters per second (approximate)
        distance_m = delay_ms*1e-3*c

        # home-made measure of the significance
        slope = 0.12
        p = 3
        x = (Xcorr_max_norm>1.)*(Xcorr_max_norm-1.)
        x = (slope*x)**p
        correlation = int((x/(1. + x))*100)
        
        delay_message = "%.1f ms = %.2f m" %(delay_ms, distance_m)

        correlation_message = "%d%%" %(correlation)

        if Xcorr_extremum >= 0:
            polarity_message = "In-phase"
        else:
            polarity_message = "Reversed phase"

        print ind, delay_message, correlation_message, polarity_message

    plt.show()

if False:
    import cProfile
    import pstats

    cProfile.runctx('main()', globals(), locals(), filename="delay.cprof")

    stats = pstats.Stats("delay.cprof")
    stats.strip_dirs().sort_stats('time').print_stats(20)
    #stats.strip_dirs().sort_stats('cumulative').print_stats(20)  
else:
    main()
