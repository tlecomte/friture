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

import numpy

class AudioData():
	def __init__ (self, rawdata, nchannels, format, samplesize, samplerate):
		self.rawdata = rawdata
		self.floatdata = numpy.fromstring(self.rawdata,numpy.int32)/2.**31
		self.nchannels = nchannels
		self.format = format
		self.samplesize = samplesize
		self.samplerate = samplerate
		self.nframes = len(self.floatdata)

def concatenate(data1, data2):
    if data1 == None:
        return data2
    if data2 == None:
        return data1
    return AudioData(data1.rawdata + data2.rawdata, data1.nchannels, data1.format, data1.samplesize, data1.samplerate)
