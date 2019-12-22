#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

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

from PyQt5 import QtGui, QtCore, QtWidgets
import numpy as np
import sounddevice
from friture.audiobackend import SAMPLING_RATE, AudioBackend
from friture.generators.sweep import SweepGenerator
from friture.generators.sine import SineGenerator
from friture.generators.burst import BurstGenerator
from friture.generators.pink import PinkGenerator
from friture.generators.white import WhiteGenerator

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
FRAMES_PER_BUFFER = 2 * 1024
DEFAULT_GENERATOR_KIND_INDEX = 0
RAMP_LENGTH = 3e-3  # 10 ms

(STOPPED, STARTING, PLAYING, STOPPING) = list(range(0, 4))


class Generator_Widget(QtWidgets.QWidget):

    stream_stop_ramp_finished = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)

        self.audiobuffer = None

        self.setObjectName("Generator_Widget")
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setObjectName("grid_layout")

        self.generators = []
        self.generators.append(SineGenerator(self))
        self.generators.append(WhiteGenerator(self))
        self.generators.append(PinkGenerator(self))
        self.generators.append(SweepGenerator(self))
        self.generators.append(BurstGenerator(self))

        self.combobox_generator_kind = QtWidgets.QComboBox(self)
        self.combobox_generator_kind.setObjectName("combobox_generator_kind")

        self.stacked_settings_layout = QtWidgets.QStackedLayout()

        for generator in self.generators:
            self.combobox_generator_kind.addItem(generator.name)
            self.stacked_settings_layout.addWidget(generator.settingsWidget())

        self.combobox_generator_kind.setCurrentIndex(DEFAULT_GENERATOR_KIND_INDEX)

        self.t = 0.
        self.t_start = 0.
        self.t_stop = RAMP_LENGTH
        self.state = STOPPED

        self.stream_stop_ramp_finished.connect(self.stop_stream_after_ramp)

        self.device = None
        self.stream = None

        # we will try to open all the output devices until one
        # works, starting by the default input device
        for device in AudioBackend().output_devices:
            self.logger.info("Opening the stream for device '%s'", device['name'])
            try:
                self.stream = AudioBackend().open_output_stream(device, self.audio_callback)
                self.stream.start()
                self.stream.stop()
                self.device = device
                self.logger.info("Stream opened successfully")
                break
            except Exception:
                self.logger.exception("Failed to open stream")

        self.start_stop_button = QtWidgets.QPushButton(self)

        startStopIcon = QtGui.QIcon()
        startStopIcon.addPixmap(QtGui.QPixmap(":/images-src/start.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        startStopIcon.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        startStopIcon.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Active, QtGui.QIcon.On)
        startStopIcon.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Selected, QtGui.QIcon.On)
        startStopIcon.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Disabled, QtGui.QIcon.On)
        self.start_stop_button.setIcon(startStopIcon)

        self.start_stop_button.setObjectName("generatorStartStop")
        self.start_stop_button.setText("Start")
        self.start_stop_button.setToolTip("Start/Stop generator")
        self.start_stop_button.setCheckable(True)
        self.start_stop_button.setChecked(False)

        self.grid_layout.addWidget(self.start_stop_button, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.combobox_generator_kind, 1, 0, 1, 1)
        self.grid_layout.addLayout(self.stacked_settings_layout, 2, 0, 1, 1)

        self.combobox_generator_kind.activated.connect(self.stacked_settings_layout.setCurrentIndex)
        self.start_stop_button.toggled.connect(self.start_stop_button_toggle)

        # initialize the settings dialog
        devices = AudioBackend().get_readable_output_devices_list()
        if self.device is not None:
            device_index = AudioBackend().output_devices.index(self.device)
        else:
            device_index = None
        self.settings_dialog = Generator_Settings_Dialog(self, devices, device_index)

        self.settings_dialog.combobox_output_device.currentIndexChanged.connect(self.device_changed)

#        channels = AudioBackend().get_readable_current_output_channels()
#        for channel in channels:
#            self.settings_dialog.comboBox_firstChannel.addItem(channel)
#            self.settings_dialog.comboBox_secondChannel.addItem(channel)

#        current_device = AudioBackend().get_readable_current_output_device()
#        self.settings_dialog.combobox_output_device.setCurrentIndex(current_device)

#        first_channel = AudioBackend().get_current_first_channel()
#        self.settings_dialog.comboBox_firstChannel.setCurrentIndex(first_channel)
#        second_channel = AudioBackend().get_current_second_channel()
#        self.settings_dialog.comboBox_secondChannel.setCurrentIndex(second_channel)

    def device_changed(self, index):
        device = AudioBackend().output_devices[index]

        # save current stream in case we need to restore it
        previous_stream = self.stream
        previous_device = self.device

        self.logger.info("Trying to write to output device '%s'", device['name'])

        # first see if the format is supported by PortAudio
        try:
            AudioBackend().is_output_format_supported(device, np.int16)
        except sounddevice.PortAudioError as err:
            self.on_device_change_error(previous_stream, previous_device, "Format is not supported: {0}".format(err))
            return

        try:
            self.stream = AudioBackend().open_output_stream(device, self.audio_callback)
            self.device = device
            self.stream.start()
            if self.state not in [STARTING, PLAYING]:
                self.stream.stop()
        except (sounddevice.PortAudioError, OSError) as err:
            self.on_device_change_error(previous_stream, previous_device, "Failed to open output device: {0}".format(err))
            return

        self.logger.info("Success")
        previous_stream.stop()

        self.settings_dialog.combobox_output_device.setCurrentIndex(AudioBackend().output_devices.index(self.device))

    def on_device_change_error(self, previous_stream, previous_device, message):
        self.logger.exception(message)

        if self.stream is not None:
            self.stream.stop()

        # restore previous stream
        self.stream = previous_stream
        self.device = previous_device

        # Note: the error message is a child of the settings dialog, so that
        # that dialog remains on top when the error message is closed
        error_message = QtWidgets.QErrorMessage(self.settings_dialog)
        error_message.setWindowTitle("Output device error")
        error_message.showMessage("Impossible to use the selected output device, reverting to the previous one. Reason is: " + message)

        self.settings_dialog.combobox_output_device.setCurrentIndex(AudioBackend().output_devices.index(self.device))

    def settings_called(self, checked):
        self.settings_dialog.show()

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    # slot
    def start_stop_button_toggle(self, checked):
        if checked:
            self.start_stop_button.setText("Stop")
            if self.state == STOPPED or self.state == STOPPING:
                self.state = STARTING
                self.t_start = 0.
                self.stream.start()
        else:
            self.start_stop_button.setText("Start")
            if self.state == PLAYING or self.state == STARTING:
                self.state = STOPPING
                self.t_stop = RAMP_LENGTH
                # will stop at the end of the ramp

    def stop_stream_after_ramp(self):
        self.stream.stop()

    def handle_new_data(self, floatdata):
        # we do not make anything of the input data in the generator...
        return

    def audio_callback(self, out_data, frame_count, time_info, status):
        if status:
            self.logger.info(status)

        N = frame_count

        if self.state == STOPPED:
            out_data.fill(0)
            return

        # if we cannot write any sample, return now
        if N == 0:
            return

        t = self.t + np.arange(0, N / float(SAMPLING_RATE), 1. / float(SAMPLING_RATE))

        name = self.combobox_generator_kind.currentText()

        generators = [generator for generator in self.generators if generator.name == name]

        if len(generators) == 0:
            self.logger.error("generator error : index of signal type not found")
            out_data.fill(0)
            return

        if len(generators) > 1:
            self.logger.error("generator error : 2 (or more) generators have the same name")
            out_data.fill(0)
            return

        generator = generators[0]
        floatdata = generator.signal(t)

        # add smooth ramps at start/stop to avoid undesirable bursts
        if self.state == STARTING:
            # add a ramp at the start
            t_ramp = self.t_start + np.arange(0, N / float(SAMPLING_RATE), 1. / float(SAMPLING_RATE))
            t_ramp = np.clip(t_ramp, 0., RAMP_LENGTH)
            floatdata *= t_ramp / RAMP_LENGTH
            self.t_start += N / float(SAMPLING_RATE)
            if self.t_start > RAMP_LENGTH:
                self.state = PLAYING

        if self.state == STOPPING:
            self.logger.info("stopping %f %d", self.t_stop, N)
            # add a ramp at the end
            t_ramp = self.t_stop - np.arange(0, N / float(SAMPLING_RATE), 1. / float(SAMPLING_RATE))
            t_ramp = np.clip(t_ramp, 0., RAMP_LENGTH)
            floatdata *= t_ramp / RAMP_LENGTH
            self.t_stop -= N / float(SAMPLING_RATE)

            if self.t_stop < 0.:
                self.state = STOPPED
                self.stream_stop_ramp_finished.emit()

        # output channels are interleaved
        # we output to all channels simultaneously with the same data
        maxOutputChannels = AudioBackend().get_device_outputchannels_count(self.device)
        floatdata = np.tile(floatdata, (maxOutputChannels, 1)).transpose()

        int16info = np.iinfo(np.int16)
        norm_coeff = min(abs(int16info.min), int16info.max)
        intdata = (np.clip(floatdata, int16info.min, int16info.max) * norm_coeff).astype(np.int16)

        # update the time counter
        self.t += N / float(SAMPLING_RATE)

        # data copy
        out_data[:] = intdata

    def canvasUpdate(self):
        return

    def saveState(self, settings):
        settings.setValue("generator kind", self.combobox_generator_kind.currentIndex())

        for generator in self.generators:
            generator.settingsWidget().saveState(settings)

        self.settings_dialog.saveState(settings)

    def restoreState(self, settings):
        generator_kind = settings.value("generator kind", DEFAULT_GENERATOR_KIND_INDEX, type=int)
        self.combobox_generator_kind.setCurrentIndex(generator_kind)
        self.stacked_settings_layout.setCurrentIndex(generator_kind)

        for generator in self.generators:
            generator.settingsWidget().restoreState(settings)

        self.settings_dialog.restoreState(settings)


class Generator_Settings_Dialog(QtWidgets.QDialog):

    def __init__(self, parent, devices, device_index):
        super().__init__(parent)

        self.setWindowTitle("Generator settings")

        self.form_layout = QtWidgets.QFormLayout(self)

        self.combobox_output_device = QtWidgets.QComboBox(self)
        self.combobox_output_device.setObjectName("comboBox_outputDevice")

        self.form_layout.addRow("Select the output device:", self.combobox_output_device)

        self.setLayout(self.form_layout)

        for device in devices:
            self.combobox_output_device.addItem(device)

        if device_index is not None:
            self.combobox_output_device.setCurrentIndex(device_index)

    def saveState(self, settings):
        # for the output device, we search by name instead of index, since
        # we do not know if the device order stays the same between sessions
        settings.setValue("deviceName", self.combobox_output_device.currentText())

    def restoreState(self, settings):
        device_name = settings.value("deviceName", "")
        device_index = self.combobox_output_device.findText(device_name)
        # change the device only if it exists in the device list
        if device_index >= 0:
            self.combobox_output_device.setCurrentIndex(device_index)
