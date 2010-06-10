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

		# look for input devices
		self.input_streams = self.get_input_streams()
		
		# we will try to open all the devices until one works, starting by the default input device
		for i, stream in enumerate(self.input_streams):
			self.logger.push("Opening the stream")
			self.open_stream(i)

			# note that this is actually the same call independently of the channel selected
			dev = stream['device']
			channel = stream['channel']
			self.logger.push("Trying to read from input device %d, channel %d" % (dev, channel))
			if self.try_input_stream():
				self.logger.push("Success")
				break
			else:
				self.logger.push("Fail")
	
	# method
	def get_readable_stream_list(self):
		stream_list = []
		
		default_device_index = self.get_default_input_device()
		
		for i, stream in enumerate(self.input_streams):
			dev_index = stream['device']
			channel = stream['channel']
			dev_info = self.pa.get_device_info_by_index(dev_index)
			api = self.pa.get_host_api_info_by_index(dev_info['hostApi'])['name']
			
			if channel is 0:
				channel_string = 'L'
			elif channel is 1:
				channel_string = 'R'	
			else:
				channel_string = "Channel %d" %channel
			
			if dev_index is default_device_index:
				extra_info = ' (system default)'
			else:
				extra_info = ''
			
			desc = "%d: (%s) %s (%s) %s" %(i, api, dev_info['name'], channel_string, extra_info)
			
			stream_list += [desc]			

		return stream_list

	# method
	def get_default_input_device(self):
		return self.pa.get_default_input_device_info()['index']

	# method
	def get_device_count(self):
		# FIXME only input devices should be chosen, not all of them !
		return self.pa.get_device_count()

	# method
	def get_input_streams(self):
		input_streams = []
		
		device_count = self.get_device_count()
		default_input_device = self.get_default_input_device()
		
		device_range = range(0, device_count)
		# start by the default input device
		device_range.remove(default_input_device)
		device_range = [default_input_device] + device_range		
		
		for i in device_range:
			dev_info = self.pa.get_device_info_by_index(i)
			for n in range(0, dev_info['maxInputChannels']):
				input_streams += [{'device': i, 'channel': n}]
				
		return input_streams

	# method
	def select_input_stream(self, index):
		# save current stream in case we need to restore it
		previous_stream = self.stream
		previous_index = self.stream_index

		self.open_stream(index)

		self.logger.push("Trying to read from input stream #%d" % (index))
		if self.try_input_stream():
			self.logger.push("Success")
			previous_stream.close()
			success = True
		else:
			self.logger.push("Fail")
			self.stream.close()
			self.stream = previous_stream
			self.stream_index = previous_index
			success = False

		return success, self.stream_index

	# method
	def open_stream(self, stream_index):
		index = self.input_streams[stream_index]['device']
		# by default we open the device stream with all the channels
		# (interleaved in the data buffer)
		maxInputChannels = self.pa.get_device_info_by_index(index)['maxInputChannels']
		self.stream = self.pa.open(format=paInt16, channels=maxInputChannels, rate=SAMPLING_RATE, input=True,
				frames_per_buffer=FRAMES_PER_BUFFER, input_device_index=index)
		self.stream_index = stream_index

	# method
	def get_current_stream(self):
		return self.stream_index

	def get_current_stream_channel(self):
		return self.input_streams[self.stream_index]['channel']
	
	def get_current_stream_nchannels(self):
		index = self.input_streams[self.stream_index]['device']
		return self.pa.get_device_info_by_index(index)['maxInputChannels']

	# method
	# return True on success
	def try_input_stream(self):
		n_try = 0
		while self.stream.get_read_available() < FRAMES_PER_BUFFER and n_try < 1000000:
			n_try +=1

		if n_try == 1000000:
			return False
		else:
			lat_ms = 1000*self.stream.get_input_latency()
			self.logger.push("Device claims %d ms latency" %(lat_ms))
			return True
