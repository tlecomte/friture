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

from PyQt5 import QtCore
from pyaudio import PyAudio, paInt16, paInputOverflow
from numpy import ndarray, int16, fromstring, vstack, iinfo, float64

# the sample rate below should be dynamic, taken from PyAudio/PortAudio
SAMPLING_RATE = 48000
FRAMES_PER_BUFFER = 512


class AudioBackend(QtCore.QObject):

    underflow = QtCore.pyqtSignal()
    new_data_available_from_callback = QtCore.pyqtSignal(bytes, int, float, int)
    new_data_available = QtCore.pyqtSignal(ndarray, float, int)

    def callback(self, in_data, frame_count, time_info, status):
        # do the minimum from here to prevent overflows, just pass the data to the main thread

        input_time = time_info['input_buffer_adc_time']

        # some API drivers in PortAudio do not return a valid time, so fallback to the current stream time
        if input_time == 0.:
            input_time = time_info['current_time']
        if input_time == 0.:
            input_time = self.stream.get_time()

        self.new_data_available_from_callback.emit(in_data, frame_count, input_time, status)

        return (None, 0)

    def __init__(self, logger):
        QtCore.QObject.__init__(self)

        self.logger = logger

        self.duo_input = False
        self.terminated = False

        self.logger.push("Initializing PyAudio")
        self.pa = PyAudio()

        # look for devices
        self.input_devices = self.get_input_devices()
        self.output_devices = self.get_output_devices()

        self.device = None
        self.first_channel = None
        self.second_channel = None

        # we will try to open all the input devices until one
        # works, starting by the default input device
        for device in self.input_devices:
            self.logger.push("Opening the stream")
            try:
                self.stream = self.open_stream(device)
                self.stream.start_stream()
                self.device = device
                self.logger.push("Success")
                break
            except:
                self.logger.push("Fail")

        if self.device is not None:
            self.first_channel = 0
            nchannels = self.get_current_device_nchannels()
            if nchannels == 1:
                self.second_channel = 0
            else:
                self.second_channel = 1

        # counter for the number of input buffer overflows
        self.xruns = 0

        self.chunk_number = 0

        self.new_data_available_from_callback.connect(self.handle_new_data)

    def close(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if not self.terminated:
            # call terminate on PortAudio
            self.logger.push("Terminating PortAudio")
            self.pa.terminate()
            self.logger.push("PortAudio terminated")

            # avoid calling PortAudio methods in the callback/slots
            self.terminated = True

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

            desc = "%s (%d channels) (%s) %s" % (dev_info['name'], nchannels, api, extra_info)

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

            desc = "%s (%d channels) (%s) %s" % (dev_info['name'], nchannels, api, extra_info)

            devices_list += [desc]

        return devices_list

    # method
    def get_default_input_device(self):
        try:
            index = self.pa.get_default_input_device_info()['index']
        except IOError:
            index = None

        return index

    # method
    def get_default_output_device(self):
        try:
            index = self.pa.get_default_output_device_info()['index']
        except IOError:
            index = None
        return index

    # method
    def get_device_count(self):
        return self.pa.get_device_count()

    # method
    # returns a list of input devices index, starting with the system default
    def get_input_devices(self):
        device_count = self.get_device_count()
        device_range = list(range(0, device_count))

        default_input_device = self.get_default_input_device()

        if default_input_device is not None:
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
        device_range = list(range(0, device_count))

        default_output_device = self.get_default_output_device()

        if default_output_device is not None:
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

    # method.
    # The index parameter is the index in the self.input_devices list of devices !
    # The return parameter is also an index in the same list.
    def select_input_device(self, index):
        device = self.input_devices[index]

        # save current stream in case we need to restore it
        previous_stream = self.stream
        previous_device = self.device

        self.logger.push("Trying to open input device #%d" % (index))

        try:
            self.stream = self.open_stream(device)
            self.device = device
            self.stream.start_stream()
            success = True
        except:
            self.logger.push("Fail")
            success = False
            if self.stream is not None:
                self.stream.close()
            # restore previous stream
            self.stream = previous_stream
            self.device = previous_device

        if success:
            self.logger.push("Success")
            previous_stream.close()

            self.first_channel = 0
            nchannels = self.get_current_device_nchannels()
            if nchannels == 1:
                self.second_channel = 0
            else:
                self.second_channel = 1

        return success, self.input_devices.index(self.device)

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
        max_input_channels = self.pa.get_device_info_by_index(device)['maxInputChannels']
        stream = self.pa.open(format=paInt16, channels=max_input_channels, rate=SAMPLING_RATE, input=True,
                              input_device_index=device, stream_callback=self.callback,
                              frames_per_buffer=FRAMES_PER_BUFFER)

        lat_ms = 1000 * stream.get_input_latency()
        self.logger.push("Device claims %d ms latency" % (lat_ms))

        return stream

    # method
    def open_output_stream(self, device, callback):
        # by default we open the device stream with all the channels
        # (interleaved in the data buffer)
        max_output_channels = self.pa.get_device_info_by_index(device)['maxOutputChannels']
        stream = self.pa.open(format=paInt16, channels=max_output_channels, rate=SAMPLING_RATE, output=True,
                              frames_per_buffer=FRAMES_PER_BUFFER, output_device_index=device,
                              stream_callback=callback)
        return stream

    def is_output_format_supported(self, device, output_format):
        max_output_channels = self.pa.get_device_info_by_index(device)['maxOutputChannels']
        success = self.pa.is_format_supported(SAMPLING_RATE, output_device=device, output_channels=max_output_channels, output_format=output_format)
        return success

    # method
    # return the index of the current input device in the input devices list
    # (not the same as the PortAudio index, since the latter is the index
    # in the list of *all* devices, not only input ones)
    def get_readable_current_device(self):
        return self.input_devices.index(self.device)

    # method
    def get_readable_current_channels(self):
        dev_info = self.pa.get_device_info_by_index(self.device)
        nchannels = dev_info['maxInputChannels']

        if nchannels == 2:
            channels = ['L', 'R']
        else:
            channels = []
            for channel in range(0, dev_info['maxInputChannels']):
                channels += ["%d" % channel]

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

    def get_device_outputchannels_count(self, device):
        return self.pa.get_device_info_by_index(device)['maxOutputChannels']

    def handle_new_data(self, in_data, frame_count, input_time, status):
        if self.terminated:
            return

        if status & paInputOverflow:
            print("Stream overflow!")
            self.xruns += 1
            self.underflow.emit()

        intdata_all_channels = fromstring(in_data, int16)

        int16info = iinfo(int16)
        norm_coeff = max(abs(int16info.min), int16info.max)
        floatdata_all_channels = intdata_all_channels.astype(float64) / float(norm_coeff)

        channel = self.get_current_first_channel()
        nchannels = self.get_current_device_nchannels()
        if self.duo_input:
            channel_2 = self.get_current_second_channel()

        if len(floatdata_all_channels) != frame_count*nchannels:
            print("Incoming data is not consistent with current channel settings.")
            return

        floatdata1 = floatdata_all_channels[channel::nchannels]

        if self.duo_input:
            floatdata2 = floatdata_all_channels[channel_2::nchannels]
            floatdata = vstack((floatdata1, floatdata2))
        else:
            floatdata = floatdata1
            floatdata.shape = (1, floatdata.size)

        self.new_data_available.emit(floatdata, input_time, status)

        self.chunk_number += 1

    def set_single_input(self):
        self.duo_input = False

    def set_duo_input(self):
        self.duo_input = True

    # returns the stream time in seconds
    def get_stream_time(self):
        return self.stream.get_time()

    def pause(self):
        self.stream.stop_stream()

    def restart(self):
        self.stream.start_stream()
