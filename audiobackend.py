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
from pyaudio import PyAudio, paInt16

# the sample rate below should be dynamic, taken from PyAudio/PortAudio
SAMPLING_RATE = 44100
FRAMES_PER_BUFFER = 1024

class AudioBackend(QtCore.QObject):
	def __init__(self, logger):
		QtCore.QObject.__init__(self)

		self.logger = logger

		self.logger.push("Initializing PyAudio")
		self.pa = PyAudio()

		device_count = self.get_device_count()
		default_device_index = self.get_default_input_device()
		
		# we will try to open all the devices until one works, starting by the default input device
		devices = range(0, device_count)
		devices.remove(default_device_index)
		devices = [default_device_index] + devices

		for index in devices:
			self.logger.push("Opening the stream")
			self.open_stream(index)

			self.logger.push("Trying to read from input device #%d" % (index))
			if self.try_input_device():
				self.logger.push("Success")
				break
			else:
				self.logger.push("Fail")
	
	# method
	def get_devices(self):
		devices = []
		
		default_device_index = self.get_default_input_device()
		device_count = self.get_device_count()
		
		for i in range(0, device_count):
			dev = self.pa.get_device_info_by_index(i)
			api = self.pa.get_host_api_info_by_index(dev['hostApi'])['name']
			desc = "%d: (%s) %s" %(dev['index'], api, dev['name'])
			if i == default_device_index:
				desc += ' (system default)'
			
			devices += [desc]

		return devices

	# method
	def get_default_input_device(self):
		return self.pa.get_default_input_device_info()['index']

	# method
	def get_device_count(self):
		# FIXME only input devices should be chosen, not all of them !
		return self.pa.get_device_count()

	# method
	def select_input_device(self, index):
		# save current stream in case we need to restore it
		previous_stream = self.stream
		previous_index = self.device_index

		self.open_stream(index)

		self.logger.push("Trying to read from input device #%d" % (index))
		if self.try_input_device():
			self.logger.push("Success")
			previous_stream.close()
			success = True
		else:
			self.logger.push("Fail")
			self.stream.close()
			self.stream = previous_stream
			self.device_index = previous_index
			success = False

		return success, self.device_index

	# method
	def open_stream(self, index):
		self.stream = self.pa.open(format=paInt16, channels=1, rate=SAMPLING_RATE, input=True,
				frames_per_buffer=FRAMES_PER_BUFFER, input_device_index=index)
		self.device_index = index

	# method
	def get_current_device(self):
		return self.device_index

	# method
	# return True on success
	def try_input_device(self):
		n_try = 0
		while self.stream.get_read_available() < FRAMES_PER_BUFFER and n_try < 1000000:
			n_try +=1

		if n_try == 1000000:
			return False
		else:
			lat_ms = 1000*self.stream.get_input_latency()
			self.logger.push("Device claims %d ms latency" %(lat_ms))
			return True
