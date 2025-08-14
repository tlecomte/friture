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

import numpy as np
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal

DEFAULT_SWEEP_STARTFREQUENCY = 20.
DEFAULT_SWEEP_STOPFREQUENCY = 22000.
DEFAULT_SWEEP_PERIOD_S = 1.


class SweepGenerator:
    name = "Sweep"

    def __init__(self, parent):
        self._view_model = Sweep_Generator_Settings_View_Model(parent)
    
        self._view_model.start_frequency_changed.connect(self.updateParams)
        self._view_model.stop_frequency_changed.connect(self.updateParams)
        self._view_model.peiod_changed.connect(self.updateParams)
    
        self.updateParams()
        [self.L, self.K, self.T] = self.nextParams
        self.nextParams = None
        self.timeoffset = 0.

    def view_model(self):
        return self._view_model

    def qml_file_name(self) -> str:
        return "SweepSettings.qml"
    
    def updateParams(self):
        self.nextParams = self.computeParams(
            self._view_model.start_frequency,
            self._view_model.stop_frequency,
            self._view_model.period)

    def computeParams(self, f1, f2, T):
        # adjust T so that we have an integer number of periods
        # we want phase_max to be a multiple of 2*np.pi
        # phase_max = 2*np.pi*f1*T/np.log(f2/f1)*(f2/f1 - 1.)
        # phase_max = N*2*np.pi
        # N = f1*T/np.log(f2/f1)*(f2/f1 - 1.)
        Tmult = np.log(f2 / f1) / (f1 * (f2 / f1 - 1.))
        if T >= Tmult:
            T = np.round(T / Tmult) * Tmult
        else:
            T = np.ceil(T / Tmult) * Tmult

        w1 = 2 * np.pi * f1
        w2 = 2 * np.pi * f2
        K = w1 * T / np.log(w2 / w1)
        L = T / np.log(w2 / w1)
        return [L, K, T]

    def signal(self, t):
        # https://ccrma.stanford.edu/realsimple/imp_meas/Sine_Sweep_Measurement_Theory.html

        # f = (self.f2 - self.f1)*(1. + np.sin(2*np.pi*t/self.T))/2. + self.f1
        # return np.sin(2*np.pi*t*f)

        result = np.cos(self.K * (np.exp((t - self.timeoffset) % self.T / self.L) - 1.))

        if self.nextParams is not None:
            # we have new params to put in place
            # do it at the first max

            diff = result[1:] - result[:-1]
            maxdetection = 0. * diff[:-1] + (diff[1:] < 0.) * (diff[:-1] > 0.) * 1.

            maxdetections = np.argwhere(maxdetection != 0.)

            if len(maxdetections) > 0:
                firstmaxpos = np.argwhere(maxdetection != 0.)[0][0] + 1

                # the first samples use the previous parameters
                # the next samples use the new parameters
                [self.L, self.K, self.T] = self.nextParams
                self.nextParams = None
                self.timeoffset = t[firstmaxpos]
                result[firstmaxpos:] = np.cos(self.K * (np.exp((t[firstmaxpos:] - self.timeoffset) % self.T / self.L) - 1.))

        return result

class Sweep_Generator_Settings_View_Model(QObject):
    start_frequency_changed = pyqtSignal(float)
    stop_frequency_changed = pyqtSignal(float)
    peiod_changed = pyqtSignal(float)

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self._start_frequency = DEFAULT_SWEEP_STARTFREQUENCY
        self._stop_frequency = DEFAULT_SWEEP_STOPFREQUENCY
        self._period = DEFAULT_SWEEP_PERIOD_S

    @pyqtProperty(float, notify=start_frequency_changed)
    def start_frequency(self) -> float:
        return self._start_frequency

    @start_frequency.setter # type: ignore
    def start_frequency(self, frequency: float):
        if self._start_frequency != frequency:
            self._start_frequency = frequency
            self.start_frequency_changed.emit(frequency)

    @pyqtProperty(float, notify=stop_frequency_changed)
    def stop_frequency(self) -> float:
        return self._stop_frequency
    
    @stop_frequency.setter # type: ignore
    def stop_frequency(self, frequency: float):
        if self._stop_frequency != frequency:
            self._stop_frequency = frequency
            self.stop_frequency_changed.emit(frequency)

    @pyqtProperty(float, notify=peiod_changed)
    def period(self) -> float:
        return self._period
    
    @period.setter # type: ignore
    def period(self, period: float):
        if self._period != period:
            self._period = period
            self.peiod_changed.emit(period)

    def saveState(self, settings):
        settings.setValue("sweep start frequency", self.start_frequency)
        settings.setValue("sweep stop frequency", self.stop_frequency)
        settings.setValue("sweep period", self.period)

    def restoreState(self, settings):
        self.start_frequency = settings.value("sweep start frequency", DEFAULT_SWEEP_STARTFREQUENCY, type=int)
        self.stop_frequency = settings.value("sweep stop frequency", DEFAULT_SWEEP_STOPFREQUENCY, type=int)
        self.period = settings.value("sweep period", DEFAULT_SWEEP_PERIOD_S, type=float)
