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

from PyQt4 import QtCore
from numpy import floor, zeros, int16, fromstring

FRAMES_PER_BUFFER = 1024

class AudioBuffer():
	def __init__(self):
		# FIXME the buffer length could be made dynamic based on the
		# needs
		self.buffer_length = 100000.
		self.audiobuffer = zeros(2*self.buffer_length)
		self.offset = 0
		self.newpoints = 0

	# try to update the audio buffer
	# return the number of chunks retrieved, and the time elapsed
	def update(self, stream, channel, nchannels):
		t = QtCore.QTime()
		t.start()
		
		chunks = 0
		
		# ask for how much data is available
		available = stream.get_read_available()
		# read what is available
		# we read by multiples of FRAMES_PER_BUFFER, otherwise segfaults !
		available = int(floor(available/FRAMES_PER_BUFFER))
		for j in range(0, available):
			chunks += 1
			try:
				rawdata = stream.read(FRAMES_PER_BUFFER)
			except IOError as inst:
				# FIXME specialize this exception handling code
				# to treat overflow errors particularly
				print inst
				print "Caught an IOError on stream read."
				break
			floatdata = fromstring(rawdata, int16)[channel::nchannels]/(2.**(16-1))
			#uncomment the following line to make difference measurements !!
			#floatdata -= fromstring(rawdata, int16)[channel+1::nchannels]/(2.**(16-1))
			
			# update the circular buffer
			if len(floatdata) > self.buffer_length:
				print "buffer error"
				exit(1)
			
			# first copy, always complete
			self.audiobuffer[self.offset : self.offset + len(floatdata)] = floatdata[:]
			# second copy, can be folded
			direct = min(len(floatdata), self.buffer_length - self.offset)
			folded = len(floatdata) - direct
			self.audiobuffer[self.offset + self.buffer_length: self.offset + self.buffer_length + direct] = floatdata[0 : direct]
			self.audiobuffer[:folded] = floatdata[direct:]
			
			self.offset = int((self.offset + len(floatdata)) % self.buffer_length)

		# holds the number of points acquired at the last update iteration
		self.newpoints = chunks*FRAMES_PER_BUFFER

		return (chunks, t.elapsed())

	def data(self, length):
		start = self.offset + self.buffer_length - length
		stop = self.offset + self.buffer_length
		return self.audiobuffer[start : stop]

	def newdata(self):
		return self.data(self.newpoints)
