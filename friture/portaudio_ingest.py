#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

# PortAudio capture adapter — loaded only when production ingest is created.

import logging
import math

import numpy as np
import rtmixer
import sounddevice
from numpy import (
    concatenate,
    float32,
    float64,
    frombuffer,
    int8,
    int16,
    ndarray,
    vstack,
)
from PyQt5 import QtCore

from friture.audio_ingest import FRAMES_PER_BUFFER, SAMPLING_RATE


class PortAudioIngest(QtCore.QObject):

    underflow = QtCore.pyqtSignal()
    new_data_available = QtCore.pyqtSignal(ndarray, float, bool)

    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger(__name__)

        self.duo_input = False

        self.logger.info("Initializing PortAudio ingest")

        self.input_devices = self.get_input_devices()
        self.output_devices = self.get_output_devices()

        self.logger.info(
            "Found %d input devices and %d output devices",
            len(self.input_devices),
            len(self.output_devices),
        )

        self.device = None
        self.first_channel = None
        self.second_channel = None

        self.stream = None
        self.ringBuffer = None
        self.action = None
        self.nchannels_max = 0
        self.stream_start_time = 0.0
        self.stream_read_index = 0

        for device in self.input_devices:
            try:
                (self.stream, self.ringBuffer, self.action, self.nchannels_max) = (
                    self.open_stream(device)
                )
                self.stream.start()
                self.device = device
                self.stream_start_time = self.stream.time
                self.stream_read_index = 0
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

        self.xruns = 0
        self.chunk_number = 0
        self.devices_with_timing_errors = []

    def close(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream = None

    def get_readable_devices_list(self):
        input_devices = self.get_input_devices()

        raw_devices = sounddevice.query_devices()

        try:
            default_input_device = sounddevice.query_devices(kind="input")
            default_input_device["index"] = raw_devices.index(default_input_device)
        except sounddevice.PortAudioError:
            self.logger.exception("Failed to query the default input device")
            default_input_device = None

        devices_list = []
        for device in input_devices:
            api = sounddevice.query_hostapis(device["hostapi"])["name"]

            if (
                default_input_device is not None
                and device["index"] == default_input_device["index"]
            ):
                extra_info = " (default)"
            else:
                extra_info = ""

            nchannels = device["max_input_channels"]

            desc = "%s (%d channels) (%s) %s" % (
                device["name"],
                nchannels,
                api,
                extra_info,
            )

            devices_list += [desc]

        return devices_list

    def get_readable_output_devices_list(self):
        output_devices = self.get_output_devices()

        raw_devices = sounddevice.query_devices()
        default_output_device = sounddevice.query_devices(kind="output")
        default_output_device["index"] = raw_devices.index(default_output_device)

        devices_list = []
        for device in output_devices:
            api = sounddevice.query_hostapis(device["hostapi"])["name"]

            if (
                default_output_device is not None
                and device["index"] == default_output_device["index"]
            ):
                extra_info = " (default)"
            else:
                extra_info = ""

            nchannels = device["max_output_channels"]

            desc = "%s (%d channels) (%s) %s" % (
                device["name"],
                nchannels,
                api,
                extra_info,
            )

            devices_list += [desc]

        return devices_list

    def get_default_input_device(self):
        try:
            index = sounddevice.default.device[0]
        except IOError:
            index = None

        return index

    def get_default_output_device(self):
        try:
            index = sounddevice.default.device[1]
        except IOError:
            index = None

        return index

    def get_input_devices(self):
        devices = sounddevice.query_devices()

        input_devices = [
            device for device in devices if device["max_input_channels"] > 0
        ]

        if len(input_devices) == 0:
            return []

        try:
            default_input_device = sounddevice.query_devices(kind="input")
        except sounddevice.PortAudioError:
            self.logger.exception("Failed to query the default input device")
            default_input_device = None

        input_devices = []
        if default_input_device is not None:
            default_input_device["index"] = devices.index(default_input_device)
            input_devices += [default_input_device]

        for device in devices:
            if device["max_input_channels"] > 0:
                device["index"] = devices.index(device)
                if (
                    default_input_device is not None
                    and device["index"] != default_input_device["index"]
                ):
                    input_devices += [device]

        return input_devices

    def get_output_devices(self):
        devices = sounddevice.query_devices()

        default_output_device = sounddevice.query_devices(kind="output")

        output_devices = []
        if default_output_device is not None:
            default_output_device["index"] = devices.index(default_output_device)
            output_devices += [default_output_device]

        for device in devices:
            if device["max_output_channels"] > 0:
                device["index"] = devices.index(device)
                if (
                    default_output_device is not None
                    and device["index"] != default_output_device["index"]
                ):
                    output_devices += [device]

        return output_devices

    def select_input_device(self, index):
        device = self.input_devices[index]

        previous_stream = self.stream
        previous_ringBuffer = self.ringBuffer
        previous_action = self.action
        previous_nchannels_max = self.nchannels_max
        previous_device = self.device

        self.logger.info("Trying to open input device #%d", index)

        try:
            (self.stream, self.ringBuffer, self.action, self.nchannels_max) = (
                self.open_stream(device)
            )
            self.device = device
            self.stream.start()
            self.stream_start_time = self.stream.time
            self.stream_read_index = 0
            success = True
        except Exception:
            self.logger.exception("Failed to open input device")
            success = False
            if self.stream is not None:
                self.stream.stop()
            self.stream = previous_stream
            self.ringBuffer = previous_ringBuffer
            self.action = previous_action
            self.nchannels_max = previous_nchannels_max
            self.device = previous_device

        if success:
            self.logger.info("Success")

            if previous_stream is not None:
                previous_stream.stop()

            self.first_channel = 0
            nchannels = self.device["max_input_channels"]
            if nchannels == 1:
                self.second_channel = 0
            else:
                self.second_channel = 1

        return success, self.input_devices.index(self.device)

    def select_first_channel(self, index):
        self.first_channel = index
        success = True
        return success, self.first_channel

    def select_second_channel(self, index):
        self.second_channel = index
        success = True
        return success, self.second_channel

    def open_stream(self, device):
        self.log_supported_input_formats(device)

        self.logger.info("Opening the stream for device '%s'", device["name"])

        stream = rtmixer.Recorder(
            device=device["index"],
            channels=device["max_input_channels"],
            blocksize=FRAMES_PER_BUFFER,
            samplerate=SAMPLING_RATE,
        )

        sampleSize = 4
        nchannels_max = device["max_input_channels"]
        elementSize = nchannels_max * sampleSize

        ringbufferSeconds = 3.0
        ringbufferSize = 2 ** int(math.log2(ringbufferSeconds * SAMPLING_RATE))

        ringBuffer = rtmixer.RingBuffer(elementSize, ringbufferSize)

        action = stream.record_ringbuffer(ringBuffer)

        lat_ms = 1000 * stream.latency
        self.logger.info("Device claims %d ms latency", lat_ms)

        return (stream, ringBuffer, action, nchannels_max)

    def log_supported_input_formats(self, device):
        samplerates = [22050, 44100, 48000, 96000]
        dtypes = [float32, int16, int8]
        supported_formats = []
        for samplerate in samplerates:
            for dtype in dtypes:
                try:
                    sounddevice.check_input_settings(
                        device=device["index"],
                        channels=device["max_input_channels"],
                        dtype=dtype,
                        extra_settings=None,
                        samplerate=samplerate,
                    )
                    supported_formats += [
                        f"{samplerate} Hz, {np.dtype(dtype).name}"
                    ]
                except Exception:
                    pass

        api = sounddevice.query_hostapis(device["hostapi"])["name"]
        self.logger.info(
            "Supported formats for '%s' on '%s': %s",
            device["name"],
            api,
            supported_formats,
        )

    def open_output_stream(self, device, callback):
        stream = sounddevice.OutputStream(
            samplerate=SAMPLING_RATE,
            blocksize=FRAMES_PER_BUFFER,
            device=device["index"],
            channels=device["max_output_channels"],
            dtype=int16,
            callback=callback,
        )

        return stream

    def is_output_format_supported(self, device, output_format):
        sounddevice.check_output_settings(
            device=device["index"],
            channels=device["max_output_channels"],
            dtype=output_format,
            samplerate=SAMPLING_RATE,
        )

    def get_readable_current_device(self):
        return self.input_devices.index(self.device)

    def get_readable_current_channels(self):
        nchannels = self.device["max_input_channels"]

        if nchannels == 2:
            channels = ["L", "R"]
        else:
            channels = []
            for channel in range(0, nchannels):
                channels += ["%d" % channel]

        return channels

    def get_current_first_channel(self):
        return self.first_channel

    def get_current_second_channel(self):
        return self.second_channel

    def get_current_device_nchannels(self):
        return self.device["max_input_channels"]

    def get_device_outputchannels_count(self, device):
        return device["max_output_channels"]

    def fetchAudioData(self):
        if self.action is None or self.ringBuffer is None:
            return

        while self.ringBuffer.read_available >= FRAMES_PER_BUFFER:
            read, buf1, buf2 = self.ringBuffer.get_read_buffers(FRAMES_PER_BUFFER)
            assert read == FRAMES_PER_BUFFER

            stream_time = self.get_stream_time()

            buffer1 = frombuffer(buf1, dtype="float32")
            buffer2 = frombuffer(buf2, dtype="float32")
            buffer = concatenate((buffer1, buffer2)).astype(float64)
            buffer.shape = -1, self.nchannels_max
            self.ringBuffer.advance_read_index(FRAMES_PER_BUFFER)

            self.stream_read_index += read
            stream_read_time = (
                self.stream_start_time + self.stream_read_index / SAMPLING_RATE
            )

            if stream_read_time > stream_time and self.stream_read_index < 100000:
                delta_seconds = stream_read_time - stream_time
                self.stream_start_time -= delta_seconds

            if (
                stream_read_time
                < stream_time - 100 * FRAMES_PER_BUFFER / SAMPLING_RATE
            ):
                self.logger.warning(
                    "Ringbuffer lagging behind: ringbuffer time = %f, stream time = %f",
                    stream_read_time,
                    stream_time,
                )

            channel = self.get_current_first_channel()
            if self.duo_input:
                channel_2 = self.get_current_second_channel()

            floatdata1 = buffer[:, channel]

            if self.duo_input:
                floatdata2 = buffer[:, channel_2]
                floatdata = vstack((floatdata1, floatdata2))
            else:
                floatdata = floatdata1
                floatdata.shape = (1, floatdata.size)

            input_overflows = self.action.stats.input_overflows
            input_overflow = input_overflows > self.xruns
            if input_overflow:
                self.xruns = input_overflows
                self.logger.info("Stream overflow!")
                self.underflow.emit()

            self.new_data_available.emit(floatdata, stream_read_time, input_overflow)

            self.chunk_number += 1

    def set_single_input(self):
        self.duo_input = False

    def set_duo_input(self):
        self.duo_input = True

    def get_stream_time(self) -> float:
        if self.stream is None:
            return 0

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
            self.stream_start_time = self.stream.time
            self.stream_read_index = 0
