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

from PyQt5 import QtGui, QtCore, QtWidgets
import numpy as np
import pyaudio
from friture.audiobackend import SAMPLING_RATE
from friture.logger import PrintLogger
from friture.generators.sweep import SweepGenerator
from friture.generators.sine import SineGenerator
from friture.generators.burst import BurstGenerator
from friture.generators.pink import PinkGenerator
from friture.generators.white import WhiteGenerator

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
FRAMES_PER_BUFFER = 2*1024
DEFAULT_GENERATOR_KIND_INDEX = 0
RAMP_LENGTH = 10e-3 # 10 ms

(stopped, starting, playing, stopping) = list(range(0, 4))

class Generator_Widget(QtWidgets.QWidget):
    def __init__(self, parent, audiobackend, logger = PrintLogger()):
        super().__init__(parent)

        self.logger = logger
        self.audiobuffer = None

        self.setObjectName("Generator_Widget")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        self.comboBox_generator_kind = QtWidgets.QComboBox(self)
        self.comboBox_generator_kind.setObjectName("comboBox_generator_kind")
        self.comboBox_generator_kind.addItem("Sine")
        self.comboBox_generator_kind.addItem("White noise")
        self.comboBox_generator_kind.addItem("Pink noise")
        self.comboBox_generator_kind.addItem("Sweep")
        self.comboBox_generator_kind.addItem("Burst")
        self.comboBox_generator_kind.setCurrentIndex(DEFAULT_GENERATOR_KIND_INDEX)

        self.sineGenerator = SineGenerator(self, logger)
        self.sweepGenerator = SweepGenerator(self, logger)
        self.whiteGenerator = WhiteGenerator(self, logger)
        self.pinkGenerator = PinkGenerator(self, logger)
        self.burstGenerator = BurstGenerator(self, logger)

        self.sinePageWidget = self.sineGenerator.settingsWidget()
        self.whitePageWidget = self.whiteGenerator.settingsWidget()
        self.pinkPageWidget = self.pinkGenerator.settingsWidget()
        self.sweepPageWidget = self.sweepGenerator.settingsWidget()
        self.burstPageWidget = self.burstGenerator.settingsWidget()

        self.stackedLayout = QtWidgets.QStackedLayout()
        self.stackedLayout.addWidget(self.sinePageWidget)
        self.stackedLayout.addWidget(self.whitePageWidget)
        self.stackedLayout.addWidget(self.pinkPageWidget)
        self.stackedLayout.addWidget(self.sweepPageWidget)
        self.stackedLayout.addWidget(self.burstPageWidget)

        self.t = 0.
        self.t_start = 0.
        self.t_stop = RAMP_LENGTH
        self.state = stopped

        self.audiobackend = audiobackend

        self.p = pyaudio.PyAudio()

        self.device = None
        self.stream = None

        # we will try to open all the input devices until one
        # works, starting by the default input device
        for device in self.audiobackend.output_devices:
            self.logger.push("Opening the stream")
            self.stream = self.open_output_stream(device)
            self.device = device

            self.logger.push("Trying to write to output device %d" %device)
            if self.test_output_stream(self.stream):
                self.logger.push("Success")
                break
            else:
                self.logger.push("Fail")

        #stream.close()
        #self.p.terminate()

        self.startStopButton = QtWidgets.QPushButton(self)

        startStopIcon = QtGui.QIcon()
        startStopIcon.addPixmap(QtGui.QPixmap(":/images-src/start.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        startStopIcon.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        startStopIcon.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Active, QtGui.QIcon.On)
        startStopIcon.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Selected, QtGui.QIcon.On)
        startStopIcon.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Disabled, QtGui.QIcon.On)
        self.startStopButton.setIcon(startStopIcon)

        self.startStopButton.setObjectName("generatorStartStop")
        self.startStopButton.setText("Start")
        self.startStopButton.setToolTip("Start/Stop generator")
        self.startStopButton.setCheckable(True)
        self.startStopButton.setChecked(False)

        self.gridLayout.addWidget(self.startStopButton, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.comboBox_generator_kind, 1, 0, 1, 1)
        self.gridLayout.addLayout(self.stackedLayout, 2, 0, 1, 1)

        self.comboBox_generator_kind.activated.connect(self.stackedLayout.setCurrentIndex)
        self.startStopButton.toggled.connect(self.startStopButton_toggle)

        #self.setStyleSheet(STYLESHEET)

        #self.response_time = DEFAULT_RESPONSE_TIME

        # initialize the settings dialog
        self.settings_dialog = Generator_Settings_Dialog(self, self.logger)

        devices = self.audiobackend.get_readable_output_devices_list()
        for device in devices:
            self.settings_dialog.comboBox_outputDevice.addItem(device)

        if self.device is not None:
            self.settings_dialog.comboBox_outputDevice.setCurrentIndex(self.audiobackend.output_devices.index(self.device))

        self.settings_dialog.comboBox_outputDevice.currentIndexChanged.connect(self.device_changed)

#        channels = self.audiobackend.get_readable_current_output_channels()
#        for channel in channels:
#            self.settings_dialog.comboBox_firstChannel.addItem(channel)
#            self.settings_dialog.comboBox_secondChannel.addItem(channel)

#        current_device = self.audiobackend.get_readable_current_output_device()
#        self.settings_dialog.comboBox_outputDevice.setCurrentIndex(current_device)

#        first_channel = self.audiobackend.get_current_first_channel()
#        self.settings_dialog.comboBox_firstChannel.setCurrentIndex(first_channel)
#        second_channel = self.audiobackend.get_current_second_channel()
#        self.settings_dialog.comboBox_secondChannel.setCurrentIndex(second_channel)

    def test_output_stream(self, stream):
        n_try = 0
        while stream.get_write_available() == 0 and n_try < 1000000:
            n_try +=1

        if n_try == 1000000:
            return False
        else:
            lat_ms = 1000*stream.get_output_latency()
            self.logger.push("Device claims %d ms latency" %(lat_ms))
            return True

    # method
    def open_output_stream(self, device):
        # by default we open the device stream with all the channels
        # (interleaved in the data buffer)
        maxOutputChannels = self.p.get_device_info_by_index(device)['maxOutputChannels']
        stream = self.p.open(format=pyaudio.paInt16, channels=maxOutputChannels, rate=SAMPLING_RATE, output=True,
                frames_per_buffer=FRAMES_PER_BUFFER, output_device_index=device)
        return stream

    def device_changed(self, device):
        # save current stream in case we need to restore it
        previous_stream = self.stream
        previous_device = self.device

        self.device = self.audiobackend.output_devices[device]
        self.stream = self.open_output_stream(self.device)

        self.logger.push("Trying to write to output device #%d" % (device))
        
        if self.test_output_stream(self.stream):
            self.logger.push("Success")
            previous_stream.close()
            success = True   
        else:
            self.logger.push("Fail")
            self.stream.close()
            self.stream = previous_stream
            self.device = previous_device
            success = False
        
        self.settings_dialog.comboBox_outputDevice.setCurrentIndex(device)
        
        if not success:
            # Note: the error message is a child of the settings dialog, so that
            # that dialog remains on top when the error message is closed
            error_message = QtWidgets.QErrorMessage(self.settings_dialog)
            error_message.setWindowTitle("Output device error")
            error_message.showMessage("Impossible to use the selected output device, reverting to the previous one")

    def settings_called(self, checked):
        self.settings_dialog.show()

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    # slot
    def startStopButton_toggle(self, checked):
        if checked:
            self.startStopButton.setText("Stop")
            if self.state == stopped or self.state == stopping:
                self.state = starting
                self.t_start = 0.
        else:
            self.startStopButton.setText("Start")
            if self.state == playing or self.state == starting:
                self.state = stopping
                self.t_stop = RAMP_LENGTH

    def handle_new_data(self, floatdata):
        # we do not make anything of the input data in the generator...
        return

    # method
    def canvasUpdate(self):
        if self.state == stopped:
            return

        if self.stream is None:
            return

        # play

        # maximum number of frames that can be written without waiting
        N = self.stream.get_write_available()
        
        # if we cannot write any sample, return now
        if N==0:
            return

        #t = self.t + np.arange(0, 5*SMOOTH_DISPLAY_TIMER_PERIOD_MS*1e-3, 1./float(SAMPLING_RATE))
        t = self.t + np.arange(0, N/float(SAMPLING_RATE), 1./float(SAMPLING_RATE))

        kind = self.comboBox_generator_kind.currentIndex()

        if kind == 0:
            floatdata = self.sineGenerator.signal(t)
        elif kind == 1:
            floatdata = self.whiteGenerator.signal(t)
        elif kind == 2:
            floatdata = self.pinkGenerator.signal(t)
        elif kind == 3:
            floatdata = self.sweepGenerator.signal(t)
        elif kind == 4:
            floatdata = self.burstGenerator.signal(t)
        else:
            print("generator error : index of signal type not found")
            return

        # add smooth ramps at start/stop to avoid undesirable bursts
        if self.state == starting:
            # add a ramp at the start
            t_ramp = self.t_start + np.arange(0, N/float(SAMPLING_RATE), 1./float(SAMPLING_RATE))
            t_ramp = np.clip(t_ramp, 0., RAMP_LENGTH)
            floatdata *= t_ramp/RAMP_LENGTH
            self.t_start += N/float(SAMPLING_RATE)
            if self.t_start > RAMP_LENGTH:
                self.state = playing
        
        if self.state == stopping:
            # add a ramp at the end
            t_ramp = self.t_stop - np.arange(0, N/float(SAMPLING_RATE), 1./float(SAMPLING_RATE))
            t_ramp = np.clip(t_ramp, 0., RAMP_LENGTH)
            floatdata *= t_ramp/RAMP_LENGTH
            self.t_stop -= N/float(SAMPLING_RATE)
            if self.t_stop < 0.:
                self.state = stopped

        # output channels are interleaved
        # we output to all channels simultaneously with the same data
        maxOutputChannels = self.p.get_device_info_by_index(self.device)['maxOutputChannels']
        floatdata = floatdata.repeat(maxOutputChannels)

        int16info = np.iinfo(np.int16)
        norm_coeff = min(abs(int16info.min), int16info.max)
        intdata = (np.clip(floatdata, int16info.min, int16info.max)*norm_coeff).astype(np.int16)
        chardata = intdata.tostring()
        self.stream.write(chardata)

        # update the time counter
        self.t += N/float(SAMPLING_RATE)

    def saveState(self, settings):
        settings.setValue("generator kind", self.comboBox_generator_kind.currentIndex())

        self.sinePageWidget.saveState(settings)
        self.whitePageWidget.saveState(settings)
        self.pinkPageWidget.saveState(settings)
        self.sweepPageWidget.saveState(settings)
        self.burstPageWidget.saveState(settings)
        self.settings_dialog.saveState(settings)

    def restoreState(self, settings):
        generator_kind = settings.value("generator kind", DEFAULT_GENERATOR_KIND_INDEX)
        self.comboBox_generator_kind.setCurrentIndex(generator_kind)
        self.stackedLayout.setCurrentIndex(generator_kind)

        self.sinePageWidget.restoreState(settings)
        self.whitePageWidget.restoreState(settings)
        self.pinkPageWidget.restoreState(settings)
        self.sweepPageWidget.restoreState(settings)
        self.burstPageWidget.restoreState(settings)
        self.settings_dialog.restoreState(settings)

class Generator_Settings_Dialog(QtWidgets.QDialog):
    def __init__(self, parent, logger):
        super().__init__(parent)

        self.logger = logger

        self.setWindowTitle("Generator settings")

        self.formLayout = QtWidgets.QFormLayout(self)

        self.comboBox_outputDevice = QtWidgets.QComboBox(self)
        self.comboBox_outputDevice.setObjectName("comboBox_outputDevice")

        self.formLayout.addRow("Select the output device:", self.comboBox_outputDevice)

        self.setLayout(self.formLayout)

    def saveState(self, settings):
        # for the output device, we search by name instead of index, since
        # we do not know if the device order stays the same between sessions
        settings.setValue("deviceName", self.comboBox_outputDevice.currentText())

    def restoreState(self, settings):
        device_name = settings.value("deviceName", "")
        id = self.comboBox_outputDevice.findText(device_name)
        # change the device only if it exists in the device list
        if id >= 0:
            self.comboBox_outputDevice.setCurrentIndex(id)
