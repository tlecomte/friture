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

from numpy import log10, array, where

from friture.filter import (octave_filter_bank_decimation, octave_frequencies,
                            octave_filter_bank_decimation_filtic, NOCTAVE)
from friture import generated_filters
import friture.renard as renard

class Octave_Filters():

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
