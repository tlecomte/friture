#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte
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
import math
import time

from PyQt5 import QtCore
import sounddevice
import rtmixer
from numpy import ndarray, vstack, int8, int16, float64, float32, frombuffer, concatenate
import numpy as np

try:
    from scipy import signal
except ImportError:
    signal = None

try:
    import pyaudiowpatch as pyaudio
    PYAUDIOWPATCH_AVAILABLE = True
except ImportError:
    PYAUDIOWPATCH_AVAILABLE = False

# the sample rate below should be dynamic, taken from PyAudio/PortAudio
SAMPLING_RATE = 48000
FRAMES_PER_BUFFER = 512

__audiobackendInstance = None


class DummyStats:
    def __init__(self):
        self.input_overflows = 0


class DummyAction:
    def __init__(self):
        self.stats = DummyStats()


class PyAudioLoopbackStream:
    """WASAPI Loopback stream handler for Windows using pyaudiowpatch."""
    def __init__(self, device_info, ring_buffer, action, target_samplerate=SAMPLING_RATE):
        self.device_info = device_info
        self.ring_buffer = ring_buffer
        self.action = action
        self.target_samplerate = target_samplerate
        self.device_samplerate = int(device_info.get('default_samplerate', target_samplerate))
        self.channels = device_info['max_input_channels']
        self.p = None
        self.stream = None
        self.device = device_info['index']
        self.latency = 0.02
        self._start_time = 0.0
        self.logger = logging.getLogger(__name__)

    @property
    def time(self):
        if self._start_time == 0.0:
            return 0.0
        return time.time() - self._start_time

    def _callback(self, in_data, frame_count, time_info, status):
        if status:
            self.action.stats.input_overflows += 1

        if in_data is not None:
            try:
                if self.device_samplerate == self.target_samplerate:
                    data_to_write = in_data
                    frames_to_write = frame_count
                else:
                    audio_np = np.frombuffer(in_data, dtype=np.float32)
                    audio_np = audio_np.reshape((frame_count, self.channels))
                    target_frames = int(round(frame_count * self.target_samplerate / self.device_samplerate))
                    if signal is not None:
                        resampled = signal.resample(audio_np, target_frames, axis=0).astype(np.float32)
                    else:
                        indices = np.linspace(0, frame_count - 1, target_frames)
                        resampled = np.zeros((target_frames, self.channels), dtype=np.float32)
                        for ch in range(self.channels):
                            resampled[:, ch] = np.interp(indices, np.arange(frame_count), audio_np[:, ch])
                    data_to_write = resampled.tobytes()
                    frames_to_write = target_frames

                if self.ring_buffer.write_available >= frames_to_write:
                    self.ring_buffer.write(data_to_write)
                else:
                    self.action.stats.input_overflows += 1
            except Exception:
                pass

        return (None, pyaudio.paContinue)

    def start(self):
        if self.p is None:
            self.p = pyaudio.PyAudio()

        if self.stream is None:
            self._start_time = time.time()
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.device_samplerate,
                input=True,
                input_device_index=self.device_info['index'],
                frames_per_buffer=FRAMES_PER_BUFFER,
                stream_callback=self._callback
            )
            self.stream.start_stream()
        elif self.stream.is_stopped():
            self._start_time = time.time()
            self.stream.start_stream()

    def stop(self):
        if self.stream is not None:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
            except Exception:
                pass

    def close(self):
        self.stop()
        if self.stream is not None:
            try:
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        if self.p is not None:
            try:
                self.p.terminate()
            except Exception:
                pass
            self.p = None


def AudioBackend():
    global __audiobackendInstance
    if __audiobackendInstance is None:
        __audiobackendInstance = __AudioBackend()
    return __audiobackendInstance


class __AudioBackend(QtCore.QObject):

    underflow = QtCore.pyqtSignal()
    new_data_available = QtCore.pyqtSignal(ndarray, float, bool)

    def __init__(self):
        QtCore.QObject.__init__(self)

        self.logger = logging.getLogger(__name__)
        self.duo_input = False

        self.logger.info("Initializing audio backend")

        # look for devices
        self.input_devices = self.get_input_devices()
        self.output_devices = self.get_output_devices()

        self.logger.info(f"Found {len(self.input_devices)} input devices and {len(self.output_devices)} output devices")

        self.device = None
        self.first_channel = None
        self.second_channel = None

        self.stream = None
        self.ringBuffer = None
        self.action = None
        self.nchannels_max = 0

        # we will try to open all the input devices until one
        # works, starting by the default input device
        for device in self.input_devices:
            try:
                (self.stream, self.ringBuffer, self.action, self.nchannels_max) = self.open_stream(device)
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
        self.devices_with_timing_errors = []

    def close(self):
        if self.stream is not None:
            if hasattr(self.stream, 'close'):
                self.stream.close()
            else:
                self.stream.stop()
            self.stream = None

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
            if device.get('is_loopback', False):
                nchannels = device['max_input_channels']
                desc = "%s (%d channels) (WASAPI Loopback)" % (device['name'], nchannels)
                devices_list += [desc]
                continue

            api = sounddevice.query_hostapis(device['hostapi'])['name']

            if default_input_device is not None and device['index'] == default_input_device['index']:
                extra_info = ' (default)'
            else:
                extra_info = ''

            nchannels = device['max_input_channels']
            desc = "%s (%d channels) (%s) %s" % (device['name'], nchannels, api, extra_info)
            devices_list += [desc]

        return devices_list

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

        input_devices = [device for device in devices if device['max_input_channels'] > 0]

        loopback_devices = []
        if PYAUDIOWPATCH_AVAILABLE:
            try:
                p = pyaudio.PyAudio()
                try:
                    for loopback in p.get_loopback_device_info_generator():
                        loopback_dev = {
                            'name': loopback['name'],
                            'index': loopback['index'],
                            'max_input_channels': loopback['maxInputChannels'],
                            'default_samplerate': int(loopback['defaultSampleRate']),
                            'is_loopback': True,
                            'pyaudio_info': loopback
                        }
                        loopback_devices.append(loopback_dev)
                finally:
                    p.terminate()
            except Exception:
                self.logger.exception("Failed to query WASAPI loopback devices")

        if len(input_devices) == 0 and len(loopback_devices) == 0:
            return []

        try:
            default_input_device = sounddevice.query_devices(kind='input')
        except sounddevice.PortAudioError:
            self.logger.exception("Failed to query the default input device")
            default_input_device = None

        final_input_devices = []
        if default_input_device is not None:
            default_input_device['index'] = devices.index(default_input_device)
            final_input_devices += [default_input_device]

        for device in devices:
            if device['max_input_channels'] > 0:
                device['index'] = devices.index(device)
                if default_input_device is not None and device['index'] != default_input_device['index']:
                    final_input_devices += [device]

        # Добавляем все Loopback устройства в конец списка
        final_input_devices.extend(loopback_devices)
        return final_input_devices

    def get_output_devices(self):
        devices = sounddevice.query_devices()
        default_output_device = sounddevice.query_devices(kind='output')

        output_devices = []
        if default_output_device is not None:
            default_output_device['index'] = devices.index(default_output_device)
            output_devices += [default_output_device]

        for device in devices:
            if device['max_output_channels'] > 0:
                device['index'] = devices.index(device)
                if default_output_device is not None and device['index'] != default_output_device['index']:
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
            (self.stream, self.ringBuffer, self.action, self.nchannels_max) = self.open_stream(device)
            self.device = device
            self.stream.start()
            self.stream_start_time = self.stream.time
            self.stream_read_index = 0
            success = True
        except Exception:
            self.logger.exception("Failed to open input device")
            success = False
            if self.stream is not None:
                if hasattr(self.stream, 'close'):
                    self.stream.close()
                else:
                    self.stream.stop()
            self.stream = previous_stream
            self.ringBuffer = previous_ringBuffer
            self.action = previous_action
            self.nchannels_max = previous_nchannels_max
            self.device = previous_device

        if success:
            self.logger.info("Success")
            if previous_stream is not None:
                if hasattr(previous_stream, 'close'):
                    previous_stream.close()
                else:
                    previous_stream.stop()

            self.first_channel = 0
            nchannels = self.device['max_input_channels']
            if nchannels == 1:
                self.second_channel = 0
            else:
                self.second_channel = 1

        return success, self.input_devices.index(self.device)

    def select_first_channel(self, index):
        self.first_channel = index
        return True, self.first_channel

    def select_second_channel(self, index):
        self.second_channel = index
        return True, self.second_channel

    def open_stream(self, device):
        self.log_supported_input_formats(device)
        self.logger.info("Opening the stream for device '%s'", device['name'])

        if device.get('is_loopback', False):
            sampleSize = 4  # float32
            nchannels_max = device['max_input_channels']
            elementSize = nchannels_max * sampleSize

            ringbufferSeconds = 3.
            ringbufferSize = 2**int(math.log2(ringbufferSeconds * SAMPLING_RATE))

            ringBuffer = rtmixer.RingBuffer(elementSize, ringbufferSize)
            action = DummyAction()
            stream = PyAudioLoopbackStream(device, ringBuffer, action, SAMPLING_RATE)
            return (stream, ringBuffer, action, nchannels_max)

        stream = rtmixer.Recorder(
            device=device['index'],
            channels=device['max_input_channels'],
            blocksize=FRAMES_PER_BUFFER,
            samplerate=SAMPLING_RATE)

        sampleSize = 4
        nchannels_max = device['max_input_channels']
        elementSize = nchannels_max * sampleSize

        ringbufferSeconds = 3.
        ringbufferSize = 2**int(math.log2(ringbufferSeconds * SAMPLING_RATE))

        ringBuffer = rtmixer.RingBuffer(elementSize, ringbufferSize)
        action = stream.record_ringbuffer(ringBuffer)

        lat_ms = 1000 * stream.latency
        self.logger.info("Device claims %d ms latency", lat_ms)

        return (stream, ringBuffer, action, nchannels_max)

    def log_supported_input_formats(self, device):
        if device.get('is_loopback', False):
            self.logger.info(f"Loopback device: '{device['name']}' at {device.get('default_samplerate', 48000)} Hz")
            return

        samplerates = [22050, 44100, 48000, 96000]
        dtypes = [float32, int16, int8]
        supported_formats = []
        for samplerate in samplerates:
            for dtype in dtypes:
                try:
                    sounddevice.check_input_settings(
                        device=device['index'],
                        channels=device['max_input_channels'],
                        dtype=dtype,
                        extra_settings=None,
                        samplerate=samplerate)
                    supported_formats += [f"{samplerate} Hz, {np.dtype(dtype).name}"]
                except Exception:
                    pass

        api = sounddevice.query_hostapis(device['hostapi'])['name']
        self.logger.info(f"Supported formats for '{device['name']}' on '{api}': {supported_formats}")

    def open_output_stream(self, device, callback):
        stream = sounddevice.OutputStream(
            samplerate=SAMPLING_RATE,
            blocksize=FRAMES_PER_BUFFER,
            device=device['index'],
            channels=device['max_output_channels'],
            dtype=int16,
            callback=callback)
        return stream

    def is_output_format_supported(self, device, output_format):
        sounddevice.check_output_settings(
            device=device['index'],
            channels=device['max_output_channels'],
            dtype=output_format,
            samplerate=SAMPLING_RATE)

    def get_readable_current_device(self):
        return self.input_devices.index(self.device)

    def get_readable_current_channels(self):
        nchannels = self.device['max_input_channels']
        if nchannels == 2:
            channels = ['L', 'R']
        else:
            channels = [str(channel) for channel in range(nchannels)]
        return channels

    def get_current_first_channel(self):
        return self.first_channel

    def get_current_second_channel(self):
        return self.second_channel

    def get_current_device_nchannels(self):
        return self.device['max_input_channels']

    def get_device_outputchannels_count(self, device):
        return device['max_output_channels']

    def fetchAudioData(self):
        if self.action is None or self.ringBuffer is None:
            return

        while self.ringBuffer.read_available >= FRAMES_PER_BUFFER:
            read, buf1, buf2 = self.ringBuffer.get_read_buffers(FRAMES_PER_BUFFER)
            assert read == FRAMES_PER_BUFFER

            stream_time = self.get_stream_time()

            buffer1 = frombuffer(buf1, dtype='float32')
            buffer2 = frombuffer(buf2, dtype='float32')
            buffer = concatenate((buffer1, buffer2)).astype(float64)
            buffer.shape = -1, self.nchannels_max
            self.ringBuffer.advance_read_index(FRAMES_PER_BUFFER)

            self.stream_read_index += read
            stream_read_time = self.stream_start_time + self.stream_read_index / SAMPLING_RATE

            if stream_read_time > stream_time and self.stream_read_index < 100000:
                delta_seconds = stream_read_time - stream_time
                self.stream_start_time -= delta_seconds

            if stream_read_time < stream_time - 100 * FRAMES_PER_BUFFER / SAMPLING_RATE:
                self.logger.warning("Ringbuffer lagging behind: ringbuffer time = %f, stream time = %f", stream_read_time, stream_time)

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
            if hasattr(self.stream, 'device') and self.stream.device not in self.devices_with_timing_errors:
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
