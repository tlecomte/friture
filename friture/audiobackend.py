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
from numpy import floor, int16, fromstring, vstack

# the sample rate below should be dynamic, taken from PyAudio/PortAudio
SAMPLING_RATE = 44100
FRAMES_PER_BUFFER = 1024

class AudioBackend(QtCore.QObject):
	def __init__(self, logger):
		QtCore.QObject.__init__(self)

		self.logger = logger
  
		self.duo_input = False

		self.logger.push("Initializing PyAudio")
		self.pa = PyAudio()

		# look for devices
		self.input_devices = self.get_input_devices()
		self.output_devices = self.get_output_devices()
		
		# we will try to open all the input devices until one
		# works, starting by the default input device
		for device in self.input_devices:
			self.logger.push("Opening the stream")
			self.stream = self.open_stream(device)
			self.device = device

			self.logger.push("Trying to read from input device %d" %device)
			if self.try_input_stream(self.stream):
				self.logger.push("Success")
				break
			else:
				self.logger.push("Fail")

		self.first_channel = 0
		nchannels = self.get_current_device_nchannels()
  		if nchannels == 1:
			self.second_channel = 0
		else:
   			self.second_channel = 1

	# method
	def get_readable_devices_list(self):
		devices_list = []
		
		default_device_index = self.get_default_input_device()
		
		for device in self.input_devices:
			dev_info = self.pa.get_device_info_by_index(device)
			api = self.pa.get_host_api_info_by_index(dev_info['hostApi'])['name']

			if device is default_device_index:
				extra_info = ' (system default)'
			else:
				extra_info = ''
			
			nchannels = self.pa.get_device_info_by_index(device)['maxInputChannels']
   
			desc = "%s (%d channels) (%s) %s" %(dev_info['name'], nchannels, api, extra_info)
			
			devices_list += [desc]			

		return devices_list

	# method
	def get_readable_output_devices_list(self):
		devices_list = []
		
		default_device_index = self.get_default_output_device()
		
		for device in self.output_devices:
			dev_info = self.pa.get_device_info_by_index(device)
			api = self.pa.get_host_api_info_by_index(dev_info['hostApi'])['name']

			if device is default_device_index:
				extra_info = ' (system default)'
			else:
				extra_info = ''
			
			nchannels = self.pa.get_device_info_by_index(device)['maxOutputChannels']
   
			desc = "%s (%d channels) (%s) %s" %(dev_info['name'], nchannels, api, extra_info)
			
			devices_list += [desc]			

		return devices_list

	# method
	def get_default_input_device(self):
		return self.pa.get_default_input_device_info()['index']

	# method
	def get_default_output_device(self):
		return self.pa.get_default_output_device_info()['index']

	# method
	def get_device_count(self):
		# FIXME only input devices should be chosen, not all of them !
		return self.pa.get_device_count()

	# method
	# returns a list of input devices index, starting with the system default
	def get_input_devices(self):
		device_count = self.get_device_count()
		default_input_device = self.get_default_input_device()
		
		device_range = range(0, device_count)
		# start by the default input device
		device_range.remove(default_input_device)
		device_range = [default_input_device] + device_range

		# select only the input devices by looking at the number of input channels
		input_devices = []
  		for device in device_range:
			n_input_channels = self.pa.get_device_info_by_index(device)['maxInputChannels']
			if n_input_channels > 0:
				input_devices += [device]
		
		return input_devices

	# method
	# returns a list of output devices index, starting with the system default
	def get_output_devices(self):
		device_count = self.get_device_count()
		default_output_device = self.get_default_output_device()
		
		device_range = range(0, device_count)
		# start by the default input device
		device_range.remove(default_output_device)
		device_range = [default_output_device] + device_range

		# select only the output devices by looking at the number of output channels
		output_devices = []
  		for device in device_range:
			n_output_channels = self.pa.get_device_info_by_index(device)['maxOutputChannels']
			if n_output_channels > 0:
				output_devices += [device]
		
		return output_devices

	# method
	def select_input_device(self, device):
		# save current stream in case we need to restore it
		previous_stream = self.stream
		previous_device = self.device

		self.stream = self.open_stream(device)
		self.device = device

		self.logger.push("Trying to read from input device #%d" % (device))
		if self.try_input_stream(self.stream):
			self.logger.push("Success")
			previous_stream.close()
			success = True   
   
			self.first_channel = 0
			nchannels = self.get_current_device_nchannels()
  			if nchannels == 1:				
				self.second_channel = 0
			else:
   				self.second_channel = 1
		else:
			self.logger.push("Fail")
			self.stream.close()
			self.stream = previous_stream
			self.device = previous_device
			success = False

		return success, self.device

	# method
	def select_first_channel(self, index):
		self.first_channel = index
		success = True
		return success, self.first_channel

	# method
	def select_second_channel(self, index):
		self.second_channel = index
		success = True
		return success, self.second_channel

	# method
	def open_stream(self, device):
		# by default we open the device stream with all the channels
		# (interleaved in the data buffer)
		maxInputChannels = self.pa.get_device_info_by_index(device)['maxInputChannels']
		stream = self.pa.open(format=paInt16, channels=maxInputChannels, rate=SAMPLING_RATE, input=True,
				frames_per_buffer=FRAMES_PER_BUFFER, input_device_index=device)
		return stream

	# method
	# return the index of the current input device in the input devices list
	# (not the same as the PortAudio index, since the latter is the index
	# in the list of *all* devices, not only input ones)
	def get_readable_current_device(self):
		i = 0
		for device in self.input_devices:
			if device == self.device:
				break
			else:
				i += 1
		return i

	# method
	def get_readable_current_channels(self):			
		dev_info = self.pa.get_device_info_by_index(self.device)  
		nchannels = dev_info['maxInputChannels']

		if nchannels == 2:
			channels = ['L', 'R']
		else:
			channels = []
   			for channel in range(0, dev_info['maxInputChannels']):
				channels += ["%d" %channel]			
			
		return channels

	# method
	def get_current_first_channel(self):
		return self.first_channel

	# method
	def get_current_second_channel(self):
		return self.second_channel

	# method	
	def get_current_device_nchannels(self):
		return self.pa.get_device_info_by_index(self.device)['maxInputChannels']

	# method
	# return True on success
	def try_input_stream(self, stream):
		n_try = 0
		while stream.get_read_available() < FRAMES_PER_BUFFER and n_try < 1000000:
			n_try +=1

		if n_try == 1000000:
			return False
		else:
			lat_ms = 1000*stream.get_input_latency()
			self.logger.push("Device claims %d ms latency" %(lat_ms))
			return True

  	# try to update the audio buffer
	# return the number of chunks retrieved, and the time elapsed
	def update(self, ringbuffer):
		t = QtCore.QTime()
		t.start()

		channel = self.get_current_first_channel()
		nchannels = self.get_current_device_nchannels()
  		if self.duo_input:
                            channel_2 = self.get_current_second_channel()
		
		chunks = 0
		
		# ask for how much data is available
		available = self.stream.get_read_available()

		# read what is available
		# we read by multiples of FRAMES_PER_BUFFER, otherwise segfaults !
		available = int(floor(available/FRAMES_PER_BUFFER))
		for j in range(0, available):
			chunks += 1
			try:
				rawdata = self.stream.read(FRAMES_PER_BUFFER)
			except IOError as inst:
				# FIXME specialize this exception handling code
				# to treat overflow errors particularly
				print inst
				print "Caught an IOError on stream read."
				break
			floatdata = fromstring(rawdata, int16)[channel::nchannels]/(2.**(16-1))
			if self.duo_input:                            			
                                       floatdata2 = fromstring(rawdata, int16)[channel_2::nchannels]/(2.**(16-1))
                                       floatdata = vstack((floatdata, floatdata2))
			else:   
                                       floatdata.shape = (1, FRAMES_PER_BUFFER)
			
			# update the circular buffer
			ringbuffer.push(floatdata)

		return (chunks, t.elapsed(), chunks*FRAMES_PER_BUFFER)
  
	def set_single_input(self):
		self.duo_input = False

	def set_duo_input(self):
		self.duo_input = True
