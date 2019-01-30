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

import logging

from PyQt5 import QtCore
import sounddevice
from numpy import ndarray, int16, fromstring, vstack, iinfo, float64

# the sample rate below should be dynamic, taken from PyAudio/PortAudio
SAMPLING_RATE = 48000
FRAMES_PER_BUFFER = 512

__audiobackendInstance = None

def AudioBackend():
    global __audiobackendInstance
    if __audiobackendInstance is None:
        __audiobackendInstance = __AudioBackend()
    return __audiobackendInstance

class __AudioBackend(QtCore.QObject):

    underflow = QtCore.pyqtSignal()
    new_data_available_from_callback = QtCore.pyqtSignal(ndarray, int, float, bool)
    new_data_available = QtCore.pyqtSignal(ndarray, float, bool)

    def callback(self, in_data, frame_count, time_info, status):
        # do the minimum from here to prevent overflows, just pass the data to the main thread

        if status:
            self.logger.info(status)

        # some API drivers in PortAudio do not return a valid inputBufferAdcTime (MME for example)
        # so fallback to the current stream time in that case
        if time_info.currentTime == 0. or time_info.inputBufferAdcTime == 0.:
            input_time = self.get_stream_time()
        elif time_info.inputBufferAdcTime == 0.:
            input_time = time_info.currentTime
        else:
            input_time = time_info.inputBufferAdcTime

        self.new_data_available_from_callback.emit(in_data, frame_count, input_time, status.input_overflow)

    def __init__(self):
        QtCore.QObject.__init__(self)

        self.logger = logging.getLogger(__name__)

        self.duo_input = False

        self.logger.info("Initializing audio backend")

        # look for devices
        self.input_devices = self.get_input_devices()
        self.output_devices = self.get_output_devices()

        self.device = None
        self.first_channel = None
        self.second_channel = None

        self.stream = None

        # we will try to open all the input devices until one
        # works, starting by the default input device
        for device in self.input_devices:
            try:
                self.stream = self.open_stream(device)
                self.stream.start()
                self.device = device
                self.logger.info("Success")
                break
            except Exception:
                self.logger.exception("Failed to open stream")

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

        self.devices_with_timing_errors = []

    def close(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream = None

    # method
    def get_readable_devices_list(self):
        input_devices = self.get_input_devices()

        raw_devices = sounddevice.query_devices()

        try:
            default_input_device = sounddevice.query_devices(kind='input')
            default_input_device['index'] = raw_devices.index(default_input_device)
        except sounddevice.PortAudioError:
            self.logger.exception("Failed to query the default input device")
            default_input_device = None

        devices_list = []
        for device in input_devices:
            api = sounddevice.query_hostapis(device['hostapi'])['name']

            if default_input_device is not None and device['index'] == default_input_device['index']:
                extra_info = ' (default)'
            else:
                extra_info = ''

            nchannels = device['max_input_channels']

            desc = "%s (%d channels) (%s) %s" % (device['name'], nchannels, api, extra_info)

            devices_list += [desc]

        return devices_list

    # method
    def get_readable_output_devices_list(self):
        output_devices = self.get_output_devices()

        raw_devices = sounddevice.query_devices()
        default_output_device = sounddevice.query_devices(kind='output')
        default_output_device['index'] = raw_devices.index(default_output_device)

        devices_list = []
        for device in output_devices:
            api = sounddevice.query_hostapis(device['hostapi'])['name']

            if default_output_device is not None and device['index'] == default_output_device['index']:
                extra_info = ' (default)'
            else:
                extra_info = ''

            nchannels = device['max_output_channels']

            desc = "%s (%d channels) (%s) %s" % (device['name'], nchannels, api, extra_info)

            devices_list += [desc]

        return devices_list

    # method
    def get_default_input_device(self):
        try:
            index = sounddevice.default.device[0]
        except IOError:
            index = None

        return index

    # method
    def get_default_output_device(self):
        try:
            index = sounddevice.default.device[1]
        except IOError:
            index = None

        return index

    # method
    # returns a list of input devices index, starting with the system default
    def get_input_devices(self):
        devices = sounddevice.query_devices()

        # early exit if there is no input device. Otherwise query_devices(kind='input') fails
        input_devices = [device for device in devices if device['max_input_channels'] > 0]

        if len(input_devices) == 0:
            return []

        try:
            default_input_device = sounddevice.query_devices(kind='input')
        except sounddevice.PortAudioError:
            self.logger.exception("Failed to query the default input device")
            default_input_device = None

        input_devices = []
        if default_input_device is not None:
            # start by the default input device
            default_input_device['index'] = devices.index(default_input_device)
            input_devices += [default_input_device]

        for device in devices:
            # select only the input devices by looking at the number of input channels
            if device['max_input_channels'] > 0:
                device['index'] = devices.index(device)
                # default input device has already been inserted
                if default_input_device is not None and device['index'] != default_input_device['index']:
                    input_devices += [device]

        return input_devices

    # method
    # returns a list of output devices index, starting with the system default
    def get_output_devices(self):
        devices = sounddevice.query_devices()

        default_output_device = sounddevice.query_devices(kind='output')

        output_devices = []
        if default_output_device is not None:
            # start by the default input device
            default_output_device['index'] = devices.index(default_output_device)
            output_devices += [default_output_device]

        for device in devices:
            # select only the output devices by looking at the number of output channels
            if device['max_output_channels'] > 0:
                device['index'] = devices.index(device)
                # default output device has already been inserted
                if default_output_device is not None and device['index'] != default_output_device['index']:
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

        self.logger.info("Trying to open input device #%d", index)

        try:
            self.stream = self.open_stream(device)
            self.device = device
            self.stream.start()
            success = True
        except Exception:
            self.logger.exception("Failed to open input device")
            success = False
            if self.stream is not None:
                self.stream.stop()
            # restore previous stream
            self.stream = previous_stream
            self.device = previous_device

        if success:
            self.logger.info("Success")

            if previous_stream is not None:
                previous_stream.stop()

            self.first_channel = 0
            nchannels = self.device['max_input_channels']
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
        self.logger.info("Opening the stream for device '%s'", device['name'])

        # by default we open the device stream with all the channels
        # (interleaved in the data buffer)
        stream = sounddevice.InputStream(
            samplerate=SAMPLING_RATE,
            blocksize=FRAMES_PER_BUFFER,
            device=device['index'],
            channels = device['max_input_channels'],
            dtype=int16,
            callback=self.callback)

        lat_ms = 1000 * stream.latency
        self.logger.info("Device claims %d ms latency", lat_ms)

        return stream

    # method
    def open_output_stream(self, device, callback):
        # by default we open the device stream with all the channels
        # (interleaved in the data buffer)
        stream = sounddevice.OutputStream(
            samplerate=SAMPLING_RATE,
            blocksize=FRAMES_PER_BUFFER,
            device=device['index'],
            channels = device['max_output_channels'],
            dtype=int16,
            callback=callback)

        return stream

    def is_output_format_supported(self, device, output_format):
        # raise sounddevice.PortAudioError if the format is not supported
        # the exception message contains the details, such as an invalid sample rate
        sounddevice.check_output_settings(
            device=device['index'],
            channels=device['max_output_channels'],
            dtype=output_format,
            samplerate=SAMPLING_RATE)

    # method
    # return the index of the current input device in the input devices list
    # (not the same as the PortAudio index, since the latter is the index
    # in the list of *all* devices, not only input ones)
    def get_readable_current_device(self):
        return self.input_devices.index(self.device)

    # method
    def get_readable_current_channels(self):
        nchannels = self.device['max_input_channels']

        if nchannels == 2:
            channels = ['L', 'R']
        else:
            channels = []
            for channel in range(0, nchannels):
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
        return self.device['max_input_channels']

    def get_device_outputchannels_count(self, device):
        return device['max_output_channels']

    def handle_new_data(self, in_data, frame_count, input_time, input_overflow):
        if input_overflow:
            self.logger.info("Stream overflow!")
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
            self.logger.error("Incoming data is not consistent with current channel settings.")
            return

        floatdata1 = floatdata_all_channels[channel::nchannels]

        if self.duo_input:
            floatdata2 = floatdata_all_channels[channel_2::nchannels]
            floatdata = vstack((floatdata1, floatdata2))
        else:
            floatdata = floatdata1
            floatdata.shape = (1, floatdata.size)

        self.new_data_available.emit(floatdata, input_time, input_overflow)

        self.chunk_number += 1

    def set_single_input(self):
        self.duo_input = False

    def set_duo_input(self):
        self.duo_input = True

    # returns the stream time in seconds
    def get_stream_time(self):
        try:
            return self.stream.time
        except (sounddevice.PortAudioError, OSError):
            if self.stream.device not in self.devices_with_timing_errors:
                self.devices_with_timing_errors.append(self.stream.device)
                self.logger.exception("Failed to read stream time")
            return 0

    def pause(self):
        if self.stream is not None:
            self.stream.stop()

    def restart(self):
        if self.stream is not None:
            self.stream.start()
