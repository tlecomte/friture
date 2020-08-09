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

"""Level widget that displays RMS level history."""

from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from friture.longlevels_settings import (LongLevels_Settings_Dialog,
                                         DEFAULT_LEVEL_MIN,
                                         DEFAULT_LEVEL_MAX,
                                         DEFAULT_MAXTIME,
                                         DEFAULT_RESPONSE_TIME)
from friture.audioproc import audioproc
from friture.timeplot import TimePlot
from .signal.decimate import decimate
from .ringbuffer import RingBuffer
from friture_extensions.lfilter import pyx_lfilter_float64_1D

from friture.audiobackend import SAMPLING_RATE

# signal > square > low-pass filter > filter for screen > log

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
LEVEL_TEXT_LABEL_PERIOD_MS = 1000

LEVEL_TEXT_LABEL_STEPS = LEVEL_TEXT_LABEL_PERIOD_MS / SMOOTH_DISPLAY_TIMER_PERIOD_MS


def gauss(n=11, sigma=1):
    r = range(-int(n/2), int(n/2)+1)
    return [1 / (sigma * np.sqrt(2*np.pi)) * np.exp(-float(x)**2/(2*sigma**2)) for x in r]


class Subsampler:
    def __init__(self, Ndec):
        self.Ndec = Ndec

        # to maintain non-negativeness of the subsampled signal, we use a gaussian filter here
        # (IIR ringing produces negative values)
        #[self.bdec, self.adec] = generated_filters.PARAMS['dec']
        self.bdec = np.array(gauss(11, 2.))
        self.adec = np.zeros(self.bdec.shape)
        self.adec[0] = 1.

        # build a proper array of zero initial conditions to start the subsampler
        self.zfs = []
        for i in range(self.Ndec):
            l = max(len(self.bdec), len(self.adec)) - 1
            self.zfs += [np.zeros(l)]

    def push(self, x):
        # FIXME problems when x is smaller than filter coeff

        # do not run on empty arrays, otherwise bad artefacts on the output !!
        if x.size == 0:
            return x

        x_dec = x

        # if we do not have enough samples, we need to buffer until we have enough
        # we need 2**self.Ndec samples in input for one in output

        zfs = []
        for i, zi in zip(list(range(self.Ndec)), self.zfs):
            x_dec, zf = decimate(self.bdec, self.adec, x_dec, zi=zi)
            # zf can be reused to restart the filter
            zfs.append(zf)

        self.zfs = zfs

        return x_dec


class LongLevelWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LongLevels_Widget")

        self.setObjectName("Scope_Widget")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneUp = TimePlot(self)
        self.PlotZoneUp.setObjectName("PlotZoneUp")
        self.PlotZoneUp.setverticaltitle("Level (dB FS RMS)")
        self.PlotZoneUp.sethorizontaltitle("Time (sec)")
        self.PlotZoneUp.setTrackerFormatter(lambda x, y: "%.3g sec, %.3g" % (x, y))

        self.level_min = DEFAULT_LEVEL_MIN
        self.level_max = DEFAULT_LEVEL_MAX
        self.PlotZoneUp.setverticalrange(self.level_min, self.level_max)

        self.gridLayout.addWidget(self.PlotZoneUp, 0, 0, 1, 1)

        self.audiobuffer = None

        # initialize the settings dialog
        self.settings_dialog = LongLevels_Settings_Dialog(self)

        # initialize the class instance that will do the fft
        self.proc = audioproc()

        self.level = None  # 1e-30
        self.level_rms = -200.

        self.two_channels = False

        self.i = 0

        self.old_index = 0

        #Set the initial timespan and response time
        self.length_seconds = DEFAULT_MAXTIME
        self.setresptime(DEFAULT_RESPONSE_TIME)

        # ringbuffer for the subsampled data
        self.ringbuffer = RingBuffer()

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata):
        # we need to maintain an index of where we are in the buffer
        index = self.audiobuffer.ringbuffer.offset
        self.last_data_time = self.audiobuffer.lastDataTime

        available = index - self.old_index

        if available < 0:
            # ringbuffer must have grown or something...
            available = 0
            self.old_index = index

        # if we have enough data to add a frequency column in the time-frequency plane, compute it
        needed = int(2**self.Ndec)
        realizable = int(np.floor(available / needed))

        if realizable > 0:
            for i in range(realizable):
                floatdata = self.audiobuffer.data_indexed(self.old_index, needed)

                # first channel
                y0 = floatdata[0, :]

                y0_squared = y0**2

                # subsample
                y0_squared_dec = self.subsampler.push(y0_squared)

                self.level, self.zf = pyx_lfilter_float64_1D(self.b, self.a, y0_squared_dec, self.zf)

                self.level_rms = 10. * np.log10(max(self.level, 1e-150))

                l = np.array([self.level_rms])
                l.shape = (1, 1)

                self.ringbuffer.push(l)

                self.old_index += needed

            self.time = np.arange(self.length_samples) / self.subsampled_sampling_rate

            levels = self.ringbuffer.data(self.length_samples)

            self.PlotZoneUp.setdata(self.time/1., levels[0, :])

    # method
    def canvasUpdate(self):
        # nothing to do here
        return

    def setmin(self, value):
        self.level_min = value
        self.PlotZoneUp.setverticalrange(self.level_min, self.level_max)

    def setmax(self, value):
        self.level_max = value
        self.PlotZoneUp.setverticalrange(self.level_min, self.level_max)

    def setduration(self, value):
        self.length_seconds = value
        self.length_samples = int(self.length_seconds * self.subsampled_sampling_rate)
        self.PlotZoneUp.settimerange(0., self.length_seconds)

    def setresptime(self, value):
        self.response_time = value
        # how many times we should decimate to end up with 100 points in the kernel
        self.Ndec = int(max(0, np.floor((np.log2(self.response_time * SAMPLING_RATE/100.)))))

        Ngauss = 4
        self.b = np.array(gauss(10*Ngauss+1, 2.*Ngauss))
        self.a = np.zeros(self.b.shape)
        self.a[0] = 1.
        self.zf = np.zeros(max(len(self.b), len(self.a)) - 1)

        self.subsampled_sampling_rate = SAMPLING_RATE / 2 ** (self.Ndec)
        self.subsampler = Subsampler(self.Ndec)

        if self.length_seconds: 
            self.setduration(self.length_seconds)

    # slot
    def settings_called(self, checked):
        self.settings_dialog.show()

    # method
    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    # method
    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)
