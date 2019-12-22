#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

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

from PyQt5 import QtWidgets
from numpy import log10, array, arange, where
from friture.histplot import HistPlot
from friture.octavespectrum_settings import (OctaveSpectrum_Settings_Dialog,  # settings dialog
                                             DEFAULT_SPEC_MIN,
                                             DEFAULT_SPEC_MAX,
                                             DEFAULT_WEIGHTING,
                                             DEFAULT_BANDSPEROCTAVE,
                                             DEFAULT_RESPONSE_TIME)

from friture.filter import (octave_filter_bank_decimation, octave_frequencies,
                            octave_filter_bank_decimation_filtic, NOCTAVE)

from friture_extensions.exp_smoothing_conv import pyx_exp_smoothed_value

from friture import generated_filters

from friture.audiobackend import SAMPLING_RATE

import friture.renard as renard

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25


class OctaveSpectrum_Widget(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.audiobuffer = None

        self.setObjectName("Spectrum_Widget")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneSpect = HistPlot(self)
        self.PlotZoneSpect.setObjectName("PlotZoneSpect")
        self.gridLayout.addWidget(self.PlotZoneSpect, 0, 0, 1, 1)

        self.spec_min = DEFAULT_SPEC_MIN
        self.spec_max = DEFAULT_SPEC_MAX
        self.weighting = DEFAULT_WEIGHTING
        self.response_time = DEFAULT_RESPONSE_TIME

        self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)
        self.PlotZoneSpect.setweighting(self.weighting)

        self.filters = octave_filters(DEFAULT_BANDSPEROCTAVE)
        self.dispbuffers = [0] * DEFAULT_BANDSPEROCTAVE * NOCTAVE

        # set kernel and parameters for the smoothing filter
        self.setresponsetime(self.response_time)

        # initialize the settings dialog
        self.settings_dialog = OctaveSpectrum_Settings_Dialog(self)

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    def compute_kernels(self, alphas, Ns):
        kernels = []
        for alpha, N in zip(alphas, Ns):
            kernels += [(1. - alpha) ** arange(N - 1, -1, -1)]
        return kernels

    def get_kernel(self, kernel, N):
        return

    def get_conv(self, kernel, data):
        return kernel * data

    def exp_smoothed_value(self, kernel, alpha, data, previous):
        N = len(data)
        if N == 0:
            return previous
        else:
            value = alpha * (kernel[-N:] * data).sum() + previous * (1. - alpha) ** N
            return value

    def handle_new_data(self, floatdata):
        # the behaviour of the filters functions is sometimes
        # unexpected when they are called on empty arrays
        if floatdata.shape[1] == 0:
            return

        # for now, take the first channel only
        floatdata = floatdata[0, :]

        # compute the filters' output
        y, decs_unused = self.filters.filter(floatdata)

        # compute the widget data
        sp = [pyx_exp_smoothed_value(kernel, alpha, bankdata ** 2, old) for bankdata, kernel, alpha, old in zip(y, self.kernels, self.alphas, self.dispbuffers)]

        # store result for next computation
        self.dispbuffers = sp

        sp = array(sp)

        if self.weighting is 0:
            w = 0.
        elif self.weighting is 1:
            w = self.filters.A
        elif self.weighting is 2:
            w = self.filters.B
        else:
            w = self.filters.C

        epsilon = 1e-30
        db_spectrogram = 10 * log10(sp + epsilon) + w
        self.PlotZoneSpect.setdata(self.filters.flow, self.filters.fhigh, self.filters.f_nominal, db_spectrogram)

    # method
    def canvasUpdate(self):
        if not self.isVisible():
            return

        self.PlotZoneSpect.draw()

    def setmin(self, value):
        self.spec_min = value
        self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)

    def setmax(self, value):
        self.spec_max = value
        self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)

    def setweighting(self, weighting):
        self.weighting = weighting
        self.PlotZoneSpect.setweighting(weighting)

    def setresponsetime(self, response_time):
        # time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000. #DISPLAY
        # time = 0.025 #IMPULSE setting for a sound level meter
        # time = 0.125 #FAST setting for a sound level meter
        # time = 1. #SLOW setting for a sound level meter
        self.response_time = response_time

        # an exponential smoothing filter is a simple IIR filter
        # s_i = alpha*x_i + (1-alpha)*s_{i-1}
        # we compute alpha so that the N most recent samples represent 100*w percent of the output
        w = 0.65
        decs = self.filters.get_decs()
        ns = [self.response_time * SAMPLING_RATE / dec for dec in decs]
        Ns = [2 * 4096 / dec for dec in decs]
        self.alphas = [1. - (1. - w) ** (1. / (n + 1)) for n in ns]
        # print(ns, Ns)
        self.kernels = self.compute_kernels(self.alphas, Ns)

    def setbandsperoctave(self, bandsperoctave):
        self.filters.setbandsperoctave(bandsperoctave)
        # recreate the ring buffers
        self.dispbuffers = [0] * bandsperoctave * NOCTAVE
        # reset kernel and parameters for the smoothing filter
        self.setresponsetime(self.response_time)

    def settings_called(self, checked):
        self.settings_dialog.show()

    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)


class octave_filters():

    def __init__(self, bandsperoctave):
        [self.bdec, self.adec] = generated_filters.PARAMS['dec']

        self.bdec = array(self.bdec)
        self.adec = array(self.adec)

        self.setbandsperoctave(bandsperoctave)

    def filter(self, floatdata):
        y, dec, zfs = octave_filter_bank_decimation(self.bdec, self.adec,
                                                    self.boct, self.aoct,
                                                    floatdata, zis=self.zfs)

        self.zfs = zfs

        return y, dec

    def get_decs(self):
        decs = [2 ** j for j in range(0, NOCTAVE)[::-1] for i in range(0, self.bandsperoctave)]

        return decs

    def setbandsperoctave(self, bandsperoctave):
        self.bandsperoctave = bandsperoctave
        self.nbands = NOCTAVE * self.bandsperoctave
        self.fi, self.flow, self.fhigh = octave_frequencies(self.nbands, self.bandsperoctave)
        [self.boct, self.aoct, fi, flow, fhigh] = generated_filters.PARAMS['%d' % bandsperoctave]

        self.boct = [array(f) for f in self.boct]
        self.aoct = [array(f) for f in self.aoct]

        # [self.b_nodec, self.a_nodec, fi, fl, fh] = octave_filters(self.nbands, self.bandsperoctave)

        f = self.fi
        Rc = 12200. ** 2 * f ** 2 / ((f ** 2 + 20.6 ** 2) * (f ** 2 + 12200. ** 2))
        Rb = 12200. ** 2 * f ** 3 / ((f ** 2 + 20.6 ** 2) * (f ** 2 + 12200. ** 2) * ((f ** 2 + 158.5 ** 2) ** 0.5))
        Ra = 12200. ** 2 * f ** 4 / ((f ** 2 + 20.6 ** 2) * (f ** 2 + 12200. ** 2) * ((f ** 2 + 107.7 ** 2) ** 0.5) * ((f ** 2 + 737.9 ** 2) ** 0.5))
        self.C = 0.06 + 20. * log10(Rc)
        self.B = 0.17 + 20. * log10(Rb)
        self.A = 2.0 + 20. * log10(Ra)
        self.zfs = octave_filter_bank_decimation_filtic(self.bdec, self.adec, self.boct, self.aoct)

        if bandsperoctave == 1:
            # with 1 band per octave, we would need the "R3.33" Renard series, but it does not exist.
            # However, that is not really a problem, since the numbers simply round up.
            self.f_nominal = ["%.1fk" % (f/1000) if f >= 10000
                              else "%.2fk" % (f/1000) if f >= 1000
                              else "%d" % (f)
                              for f in self.fi]
        else:
            # with more than 1 band per octave, use the preferred numbers from the Renard series
            if bandsperoctave == 3:
                basis = renard.R10
            elif bandsperoctave == 6:
                basis = renard.R20
            elif bandsperoctave == 12:
                basis = renard.R40
            elif bandsperoctave == 24:
                basis = renard.R80
            else:
                raise Exception("Unknown bandsperoctave: %d" % (bandsperoctave))

            # search the index of 1 kHz, the reference
            i = where(self.fi == 1000.)[0][0]

            # build the frequency scale
            self.f_nominal = []

            k = 0
            while len(self.f_nominal) < len(self.fi) - i:
                self.f_nominal += ["{0:.{width}f}k".format(10 ** k * f, width=2 - k) for f in basis]
                k += 1
            self.f_nominal = self.f_nominal[:len(self.fi) - i]

            k = 0
            while len(self.f_nominal) < len(self.fi):
                self.f_nominal = ["%d" % (10 ** (2 - k) * f) for f in basis] + self.f_nominal
                k += 1
            self.f_nominal = self.f_nominal[-len(self.fi):]
