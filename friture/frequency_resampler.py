# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 20:29:18 2012

@author: timothee
"""

import numpy as np
#from scipy.interpolate import interp1d, UnivariateSpline

class Frequency_Resampler:
    def __init__(self, logfreqscale=0, minfreq=20., maxfreq=20000., nsamples=1):
        self.logfreqscale = logfreqscale # 0: linear
        self.minfreq = minfreq
        self.maxfreq = maxfreq
        self.nsamples = nsamples
        self.update_xscale()

    def setfreqrange(self, minfreq, maxfreq):
        print("freq range changed", minfreq, maxfreq)
        self.minfreq = minfreq
        self.maxfreq = maxfreq
        self.update_xscale()

    def update_xscale(self):
        if self.logfreqscale == 2:
            self.xscaled = np.logspace(np.log2(self.minfreq), np.log2(self.maxfreq), self.nsamples, base=2.0)
        elif self.logfreqscale == 1:
            self.xscaled = np.logspace(np.log10(self.minfreq), np.log10(self.maxfreq), self.nsamples)
        else:
            self.xscaled = np.linspace(self.minfreq, self.maxfreq, self.nsamples)

    def setnsamples(self, nsamples):
        if self.nsamples != nsamples:
            self.nsamples = nsamples
            self.update_xscale()
            print("nsamples changed, now: %d" %(nsamples))

    def setlogfreqscale(self, logfreqscale):
        if logfreqscale != self.logfreqscale:
            print("freq scale changed", logfreqscale)
            self.logfreqscale = logfreqscale
            self.update_xscale()

    def process(self, freq, data):
        #f = interp1d(freq, data) # construct an interpolant
        #return f(self.xscaled)
        #s = UnivariateSpline(freq, data, s=0, k=1) # construct the spline
        #return s(self.xscaled)
        #Note : interp1d and UnivariateSpline are both slower than interp
        # interp is still not optimal because it involved a search whereas
        # the data is already completely sorted so an running interpolation
        # could be done faster
        return np.interp(self.xscaled, freq, data)
