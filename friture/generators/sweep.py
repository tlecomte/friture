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

class SweepGenerator:
    def __init__(self):
        self.f1 = 20.
        self.f2 = 22000.
        self.T = 1.
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)

    def computeKL(self, f1, f2, T):
        w1 = 2*np.pi*f1
        w2 = 2*np.pi*f2
        K = w1*T/np.log(w2/w1)
        L = T/np.log(w2/w1)
        return L, K

    def setf1(self, f1):
        self.f1 = f1
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)

    def setf2(self, f2):
        self.f2 = f2
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)

    def setT(self, T):
        self.T = T
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)

    def signal(self, t):
        # https://ccrma.stanford.edu/realsimple/imp_meas/Sine_Sweep_Measurement_Theory.html

        #f = (self.f2 - self.f1)*(1. + np.sin(2*np.pi*t/self.T))/2. + self.f1
        #return np.sin(2*np.pi*t*f)
        return np.sin(self.K*(np.exp(t%self.T/self.L) - 1.))
