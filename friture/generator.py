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
from numpy.random import standard_normal
from friture.audiobackend import SAMPLING_RATE
from friture.logger import PrintLogger

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25

FRAMES_PER_BUFFER = 2*1024

DEFAULT_GENERATOR_KIND_INDEX = 0
DEFAULT_SINE_FREQUENCY = 440.
DEFAULT_SWEEP_STARTFREQUENCY = 20.
DEFAULT_SWEEP_STOPFREQUENCY = 22000.
DEFAULT_BURST_PERIOD_S = 1.
DEFAULT_SWEEP_PERIOD_S = 1.

PINK_FIDELITY = 100.

RAMP_LENGTH = 10e-3 # 10 ms

(stopped, starting, playing, stopping) = list(range(0, 4))

def pinknoise(n, rvs=standard_normal):
    if n==0:
        return np.zeros((0,))
    
    #k = int(min(np.floor(np.log(n)/np.log(2)), PINK_FIDELITY))
    k = 13 # dynamic k adds audible "clicks"
    pink = np.zeros((n,), np.float)

    for m in 2**np.arange(k):
        p = int(np.ceil(float(n) / m))
        pink += np.repeat(rvs(size=p), m, axis=0)[:n]

    return pink/k

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

        sinePageWidget = QtWidgets.QWidget(self)
        whitePageWidget = QtWidgets.QWidget(self)
        pinkPageWidget = QtWidgets.QWidget(self)
        sweepPageWidget = QtWidgets.QWidget(self)
        burstPageWidget = QtWidgets.QWidget(self)

        self.stackedLayout = QtGui.QStackedLayout()
        self.stackedLayout.addWidget(sinePageWidget)
        self.stackedLayout.addWidget(whitePageWidget)
        self.stackedLayout.addWidget(pinkPageWidget)
        self.stackedLayout.addWidget(sweepPageWidget)
        self.stackedLayout.addWidget(burstPageWidget)

        self.spinBox_sine_frequency = QtGui.QSpinBox(sinePageWidget)
        self.spinBox_sine_frequency.setKeyboardTracking(False)
        self.spinBox_sine_frequency.setMinimum(20)
        self.spinBox_sine_frequency.setMaximum(22000)
        self.spinBox_sine_frequency.setProperty("value", DEFAULT_SINE_FREQUENCY)
        self.spinBox_sine_frequency.setObjectName("spinBox_sine_frequency")
        self.spinBox_sine_frequency.setSuffix(" Hz")

        self.sineLayout = QtGui.QFormLayout(sinePageWidget)
        self.sineLayout.addRow("Frequency:", self.spinBox_sine_frequency)

        self.spinBox_sweep_startfrequency = QtGui.QSpinBox(sweepPageWidget)
        self.spinBox_sweep_startfrequency.setKeyboardTracking(False)
        self.spinBox_sweep_startfrequency.setMinimum(20)
        self.spinBox_sweep_startfrequency.setMaximum(22000)
        self.spinBox_sweep_startfrequency.setProperty("value", DEFAULT_SWEEP_STARTFREQUENCY)
        self.spinBox_sweep_startfrequency.setObjectName("spinBox_sweep_startfrequency")
        self.spinBox_sweep_startfrequency.setSuffix(" Hz")

        self.spinBox_sweep_stopfrequency = QtGui.QSpinBox(sweepPageWidget)
        self.spinBox_sweep_stopfrequency.setKeyboardTracking(False)
        self.spinBox_sweep_stopfrequency.setMinimum(20)
        self.spinBox_sweep_stopfrequency.setMaximum(22000)
        self.spinBox_sweep_stopfrequency.setProperty("value", DEFAULT_SWEEP_STOPFREQUENCY)
        self.spinBox_sweep_stopfrequency.setObjectName("spinBox_sweep_stopfrequency")
        self.spinBox_sweep_stopfrequency.setSuffix(" Hz")

        self.spinBox_sweep_period = QtGui.QDoubleSpinBox(sweepPageWidget)
        self.spinBox_sweep_period.setKeyboardTracking(False)
        self.spinBox_sweep_period.setDecimals(2)
        self.spinBox_sweep_period.setSingleStep(1)
        self.spinBox_sweep_period.setMinimum(0.01)
        self.spinBox_sweep_period.setMaximum(60)
        self.spinBox_sweep_period.setProperty("value", DEFAULT_SWEEP_PERIOD_S)
        self.spinBox_sweep_period.setObjectName("spinBox_sweep_period")
        self.spinBox_sweep_period.setSuffix(" s")

        self.sweepLayout = QtGui.QFormLayout(sweepPageWidget)
        self.sweepLayout.addRow("Start frequency:", self.spinBox_sweep_startfrequency)
        self.sweepLayout.addRow("Stop frequency:", self.spinBox_sweep_stopfrequency)
        self.sweepLayout.addRow("Period:", self.spinBox_sweep_period)

        self.spinBox_burst_period = QtGui.QDoubleSpinBox(burstPageWidget)
        self.spinBox_burst_period.setKeyboardTracking(False)
        self.spinBox_burst_period.setDecimals(2)
        self.spinBox_burst_period.setSingleStep(1)
        self.spinBox_burst_period.setMinimum(0.01)
        self.spinBox_burst_period.setMaximum(60)
        self.spinBox_burst_period.setProperty("value", DEFAULT_BURST_PERIOD_S)
        self.spinBox_burst_period.setObjectName("spinBox_burst_period")
        self.spinBox_burst_period.setSuffix(" s")

        self.burstLayout = QtGui.QFormLayout(burstPageWidget)
        self.burstLayout.addRow("Period:", self.spinBox_burst_period)

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

        self.startStopButton = QtGui.QPushButton(self)

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

        if self.device != None:
            self.settings_dialog.comboBox_outputDevice.setCurrentIndex(self.audiobackend.output_devices.index(self.device))

        self.settings_dialog.comboBox_outputDevice.currentIndexChanged.connect(self.device_changed)

        self.sweepGenerator = SweepGenerator()
        self.spinBox_sweep_startfrequency.valueChanged.connect(self.sweepGenerator.setf1)
        self.spinBox_sweep_stopfrequency.valueChanged.connect(self.sweepGenerator.setf2)
        self.spinBox_sweep_period.valueChanged.connect(self.sweepGenerator.setT)
        
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
            error_message = QtGui.QErrorMessage(self.settings_dialog)
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

    # method
    def update(self):
        if self.state == stopped:
            return

        if self.stream == None:
            return

        # play

        # maximum number of frames that can be written without waiting
        N = self.stream.get_write_available()
        
        # if we cannot write any sample, return now
        if N==0:
            return

        #t = self.t + np.arange(0, 5*SMOOTH_DISPLAY_TIMER_PERIOD_MS*1e-3, 1./float(SAMPLING_RATE))
        t = self.t + np.arange(0, N/float(SAMPLING_RATE), 1./float(SAMPLING_RATE))
        n = len(t)

        kind = self.comboBox_generator_kind.currentIndex()

        if kind == 0:
            # sinusoid
            f = float(self.spinBox_sine_frequency.value())
            floatdata = np.sin(2.*np.pi*t*f)                
        elif kind == 1:
            # white noise
            floatdata = standard_normal(n)
        elif kind == 2:
            #pink noise
            floatdata = pinknoise(n)
        elif kind == 3:
            #sweep
            floatdata = self.sweepGenerator.sweepSignal(t)
        elif kind == 4:
            #burst
            floatdata = np.zeros(t.shape)
            T = self.spinBox_burst_period.value() # period
            i = (t*SAMPLING_RATE)%(T*SAMPLING_RATE)
            n = 1
            ind_plus = np.where(i < n)
            #ind_minus = np.where((i >= n)*(i < 2*n))
            floatdata[ind_plus] = 1.
            #floatdata[ind_minus] = -1.
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
        settings.setValue("sine frequency", self.spinBox_sine_frequency.value())
        settings.setValue("sweep start frequency", self.spinBox_sweep_startfrequency.value())
        settings.setValue("sweep stop frequency", self.spinBox_sweep_stopfrequency.value())
        settings.setValue("sweep period", self.spinBox_sweep_period.value())
        settings.setValue("burst period", self.spinBox_burst_period.value())
        
        self.settings_dialog.saveState(settings)

    def restoreState(self, settings):
        generator_kind = settings.value("generator kind", DEFAULT_GENERATOR_KIND_INDEX)
        self.comboBox_generator_kind.setCurrentIndex(generator_kind)
        self.stackedLayout.setCurrentIndex(generator_kind)
        sine_freq = float(settings.value("sine frequency", DEFAULT_SINE_FREQUENCY))
        self.spinBox_sine_frequency.setValue(sine_freq)
        sweep_start_frequency = float(settings.value("sweep start frequency", DEFAULT_SWEEP_STARTFREQUENCY))
        self.spinBox_sweep_startfrequency.setValue(sweep_start_frequency)
        sweep_stop_frequency = float(settings.value("sweep stop frequency", DEFAULT_SWEEP_STOPFREQUENCY))
        self.spinBox_sweep_stopfrequency.setValue(sweep_stop_frequency)
        sweep_period = float(settings.value("sweep period", DEFAULT_BURST_PERIOD_S))
        self.spinBox_sweep_period.setValue(sweep_period)
        burst_period = float(settings.value("burst period", DEFAULT_SWEEP_PERIOD_S))
        self.spinBox_burst_period.setValue(burst_period)
        
        self.settings_dialog.restoreState(settings)

class Generator_Settings_Dialog(QtWidgets.QDialog):
    def __init__(self, parent, logger):
        super().__init__(self, parent)

        self.logger = logger

        self.setWindowTitle("Spectrum settings")

        self.formLayout = QtGui.QFormLayout(self)

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

class SweepGenerator:
    def __init__(self):
        self.f1 = 20.
        self.f2 = 22000.
        self.T = 1.
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)
    
    def computeKL(self, f1, f2, T):
        w1 = 2*np.pi*f1
        w2 = 2*np.pi*f2
        K = w1*T/np.log(w2/w1)
        L = T/np.log(w2/w1)
        return L, K

    def setf1(self, f1):
        self.f1 = f1
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)
        
    def setf2(self, f2):
        self.f2 = f2
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)        

    def setT(self, T):
        self.T = T
        self.L, self.K = self.computeKL(self.f1, self.f2, self.T)
    
    def sweepSignal(self, t):
        # https://ccrma.stanford.edu/realsimple/imp_meas/Sine_Sweep_Measurement_Theory.html

        #f = (self.f2 - self.f1)*(1. + np.sin(2*np.pi*t/self.T))/2. + self.f1
        #return np.sin(2*np.pi*t*f)
        return np.sin(self.K*(np.exp(t%self.T/self.L) - 1.))
