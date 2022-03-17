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
from numpy import log10, array, arange

from friture.histplot import HistPlot
from friture.octavefilters import Octave_Filters
from friture.octavespectrum_settings import (OctaveSpectrum_Settings_Dialog,  # settings dialog
                                             DEFAULT_SPEC_MIN,
                                             DEFAULT_SPEC_MAX,
                                             DEFAULT_WEIGHTING,
                                             DEFAULT_BANDSPEROCTAVE,
                                             DEFAULT_RESPONSE_TIME)

from friture.filter import NOCTAVE

from friture_extensions.exp_smoothing_conv import pyx_exp_smoothed_value

from friture.audiobackend import SAMPLING_RATE

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25


class OctaveSpectrum_Widget(QtWidgets.QWidget):

    def __init__(self, parent, engine):
        super().__init__(parent)

        self.audiobuffer = None

        self.setObjectName("Spectrum_Widget")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.PlotZoneSpect = HistPlot(self, engine)
        self.PlotZoneSpect.setObjectName("PlotZoneSpect")
        self.gridLayout.addWidget(self.PlotZoneSpect, 0, 0, 1, 1)

        self.spec_min = DEFAULT_SPEC_MIN
        self.spec_max = DEFAULT_SPEC_MAX
        self.weighting = DEFAULT_WEIGHTING
        self.response_time = DEFAULT_RESPONSE_TIME

        self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)
        self.PlotZoneSpect.setweighting(self.weighting)

        self.filters = Octave_Filters(DEFAULT_BANDSPEROCTAVE)
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

        if self.weighting == 0:
            w = 0.
        elif self.weighting == 1:
            w = self.filters.A
        elif self.weighting == 2:
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
