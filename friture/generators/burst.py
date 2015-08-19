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
from friture.audiobackend import SAMPLING_RATE

class BurstGenerator:
    def __init__(self):
        self.T = 1.

    def setT(self, T):
        self.T = T

    def signal(self, t):
        floatdata = np.zeros(t.shape)
        i = (t*SAMPLING_RATE)%(self.T*SAMPLING_RATE)
        n = 1
        ind_plus = np.where(i < n)
        #ind_minus = np.where((i >= n)*(i < 2*n))
        floatdata[ind_plus] = 1.
        #floatdata[ind_minus] = -1.
        return floatdata
