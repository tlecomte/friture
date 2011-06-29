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

from friture.ringbuffer import RingBuffer

FRAMES_PER_BUFFER = 1024

class AudioBuffer():
	def __init__(self):
		self.ringbuffer = RingBuffer()
		self.newpoints = 0
		self.delay_samples = 0

	def data(self, length):
		return self.ringbuffer.data(length)

	def data_older(self, length, delay_samples):
		return self.ringbuffer.data_older(length, delay_samples)

	def newdata(self):
		return self.data(self.newpoints)

	def set_newdata(self, newpoints):
		self.newpoints = newpoints

	def data_delayed(self, length):
		undelayed = self.data(length)
		delayed = self.data_older(length, self.delay_samples)
		data = delayed
		data[1,:] = undelayed[1,:]
		return data

	def set_delay_ms(self, delay_ms):
		self.delay_samples = delay_ms*1e-3*44100
