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

from PyQt5 import QtGui, QtWidgets
import numpy

from friture import generated_filters
from .audiobackend import SAMPLING_RATE
from .ringbuffer import RingBuffer
from .signal.decimate import decimate_multiple, decimate_multiple_filtic
from .signal.correlation import generalized_cross_correlation

DEFAULT_DELAYRANGE = 1  # default delay range is 1 second


class Delay_Estimator_Widget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.audiobuffer = None

        self.previous_delay_message = ""
        self.previous_correlation_message = ""
        self.previous_polarity_message = ""
        self.previous_channel_info_message = ""

        self.setObjectName("Delay_Estimator_Widget")
        self.layout = QtWidgets.QFormLayout(self)
        self.layout.setObjectName("layout")

        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)

        self.delay_label = QtWidgets.QLabel(self)
        self.delay_label.setFont(font)
        self.delay_label.setObjectName("delay_label")

        self.delay_text_label = QtWidgets.QLabel(self)
        self.delay_text_label.setObjectName("delay_text_label")
        self.delay_text_label.setText("Delay:")

        self.correlation_label = QtWidgets.QLabel(self)
        self.correlation_label.setObjectName("Correlation_label")

        self.correlation_text_label = QtWidgets.QLabel(self)
        self.correlation_text_label.setObjectName("correlation_text_label")
        self.correlation_text_label.setText("Confidence:")

        self.polarity_label = QtWidgets.QLabel(self)
        self.polarity_label.setFont(font)
        self.polarity_label.setObjectName("polarity_label")

        self.polarity_text_label = QtWidgets.QLabel(self)
        self.polarity_text_label.setObjectName("polarity_text_label")
        self.polarity_text_label.setText("Polarity:")

        self.channel_info_label = QtWidgets.QLabel(self)
        self.channel_info_label.setObjectName("channel_info_label")

        self.layout.addRow(self.delay_text_label, self.delay_label)
        self.layout.addRow(self.correlation_text_label, self.correlation_label)
        self.layout.addRow(self.polarity_text_label, self.polarity_label)
        self.layout.addRow(None, self.channel_info_label)

        self.settings_dialog = Delay_Estimator_Settings_Dialog(self)

        # We will decimate several times
        # no decimation => 1/fs = 23 µs resolution
        # 1 ms resolution => fs = 1000 Hz is enough => can divide the sampling rate by 44 !
        # if I decimate 2 times (2**2 = 4 => 0.092 ms (3 cm) resolution)!
        # if I decimate 3 times (2**3 = 8 => 0.184 ms (6 cm) resolution)!
        # if I decimate 4 times (2**4 = 16 => 0.368 ms (12 cm) resolution)!
        # if I decimate 5 times (2**5 = 32 => 0.7 ms (24 cm) resolution)!
        # (actually, I could fit a gaussian on the cross-correlation peak to get
        # higher resolution even at low sample rates)
        self.Ndec = 2
        self.subsampled_sampling_rate = SAMPLING_RATE / 2 ** (self.Ndec)
        [self.bdec, self.adec] = generated_filters.PARAMS['dec']
        self.bdec = numpy.array(self.bdec)
        self.adec = numpy.array(self.adec)
        self.zfs0 = decimate_multiple_filtic(self.Ndec, self.bdec, self.adec)
        self.zfs1 = decimate_multiple_filtic(self.Ndec, self.bdec, self.adec)

        # ringbuffers for the subsampled data
        self.ringbuffer0 = RingBuffer()
        self.ringbuffer1 = RingBuffer()

        self.delayrange_s = DEFAULT_DELAYRANGE  # confidence range

        self.old_Xcorr = None

        self.old_index = 0

        self.two_channels = False
        self.delay_ms = 0.
        self.distance_m = 0.
        self.correlation = 0.
        self.Xcorr_extremum = 0.

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata):
        if floatdata.shape[0] == 1:
            self.two_channels = False
        else:
            self.two_channels = True

            # separate the channels
            x0 = floatdata[0, :]
            x1 = floatdata[1, :]
            # subsample them
            x0_dec, self.zfs0 = decimate_multiple(self.Ndec, self.bdec, self.adec, x0, self.zfs0)
            x1_dec, self.zfs1 = decimate_multiple(self.Ndec, self.bdec, self.adec, x1, self.zfs1)
            # push to a 1-second ring buffer
            x0_dec.shape = (1, x0_dec.size)
            x1_dec.shape = (1, x1_dec.size)
            self.ringbuffer0.push(x0_dec)
            self.ringbuffer1.push(x1_dec)

            # we need to maintain an index of where we are in the buffer
            index = self.ringbuffer0.offset
            available = index - self.old_index

            if available < 0:
                # ringbuffer must have grown or something...
                available = 0
                self.old_index = index

            time = 2 * self.delayrange_s
            length = time * self.subsampled_sampling_rate
            overlap = 0.5
            needed = int(overlap * length)

            realizable = int(available / needed)

            for i in range(realizable):
                self.old_index += needed

                # retrieve data
                d0 = self.ringbuffer0.data_indexed(self.old_index, int(length))
                d1 = self.ringbuffer1.data_indexed(self.old_index, int(length))
                d0.shape = (d0.size)
                d1.shape = (d1.size)
                std0 = numpy.std(d0)
                std1 = numpy.std(d1)
                if std0 > 0. and std1 > 0.:
                    Xcorr = generalized_cross_correlation(d0, d1)

                    if self.old_Xcorr is not None and self.old_Xcorr.shape == Xcorr.shape:
                        # smoothing
                        alpha = 0.3
                        smoothed_Xcorr = alpha * Xcorr + (1. - alpha) * self.old_Xcorr
                    else:
                        smoothed_Xcorr = Xcorr

                    absXcorr = numpy.abs(smoothed_Xcorr)
                    i = numpy.argmax(absXcorr)

                    # normalize
                    # Xcorr_max_norm = Xcorr_unweighted[i]/(d0.size*std0*std1)
                    self.Xcorr_extremum = smoothed_Xcorr[i]
                    Xcorr_max_norm = abs(smoothed_Xcorr[i]) / (3 * numpy.std(smoothed_Xcorr))
                    self.delay_ms = 1e3 * float(i) / self.subsampled_sampling_rate

                    # delays larger than the half of the window most likely are actually negative
                    if self.delay_ms > 1e3 * time / 2.:
                        self.delay_ms -= 1e3 * time

                    # numpy.save("Xcorr_%d_%.1f.npy" %(i,delay_ms), Xcorr)
                    # numpy.save("smoothed_Xcorr%d_%.1f.npy" %(i,delay_ms), smoothed_Xcorr)

                    # store for smoothing
                    self.old_Xcorr = smoothed_Xcorr
                else:
                    self.delay_ms = 0.
                    Xcorr_max_norm = 0.
                    self.Xcorr_extremum = 0.

                # debug wrong phase detection
                # if Xcorr[i] < 0.:
                #    numpy.save("Xcorr.npy", Xcorr)

                c = 340.  # speed of sound, in meters per second (approximate)
                self.distance_m = self.delay_ms * 1e-3 * c

                # home-made measure of the significance
                slope = 0.12
                p = 3
                x = (Xcorr_max_norm > 1.) * (Xcorr_max_norm - 1.)
                x = (slope * x) ** p
                self.correlation = int((x / (1. + x)) * 100)

    # method
    def canvasUpdate(self):
        if not self.isVisible():
            return

        if self.two_channels:
            delay_message = "%.1f ms\n= %.2f m" % (self.delay_ms, self.distance_m)
            correlation_message = "%d%%" % (self.correlation)
            if self.Xcorr_extremum >= 0:
                polarity_message = "In-phase"
            else:
                polarity_message = "Reversed phase"
            channelInfo_message = ""

            if delay_message != self.previous_delay_message:
                self.delay_label.setText(delay_message)
                self.previous_delay_message = delay_message
            if correlation_message != self.previous_correlation_message:
                self.correlation_label.setText(correlation_message)
                self.previous_correlation_message = correlation_message
            if polarity_message != self.previous_polarity_message:
                self.polarity_label.setText(polarity_message)
                self.previous_polarity_message = polarity_message
            if channelInfo_message != self.previous_channel_info_message:
                self.channel_info_label.setText(channelInfo_message)
                self.previous_channel_info_message = channelInfo_message
        else:
            message = """Delay estimator only works
with two channels.
Select two-channels mode
in the setup window."""
            if message != self.previous_channel_info_message:
                self.previous_delay_message = "N/A ms\n(N/A m)"
                self.delay_label.setText(self.previous_delay_message)
                self.previous_correlation_message = "N/A %"
                self.correlation_label.setText(self.previous_correlation_message)
                self.previous_polarity_message = "N/A"
                self.polarity_label.setText(self.previous_polarity_message)
                self.channel_info_label.setText(message)
                self.previous_channel_info_message = message

    def set_delayrange(self, delay_s):
        self.delayrange_s = delay_s

    # slot
    def settings_called(self, checked):
        self.settings_dialog.show()

    # method
    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    # method
    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)


class Delay_Estimator_Settings_Dialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Delay estimator settings")

        self.form_layout = QtWidgets.QFormLayout(self)

        self.double_spinbox_delayrange = QtWidgets.QDoubleSpinBox(self)
        self.double_spinbox_delayrange.setDecimals(1)
        self.double_spinbox_delayrange.setMinimum(0.1)
        self.double_spinbox_delayrange.setMaximum(1000.0)
        self.double_spinbox_delayrange.setProperty("value", DEFAULT_DELAYRANGE)
        self.double_spinbox_delayrange.setObjectName("double_spinbox_delayrange")
        self.double_spinbox_delayrange.setSuffix(" s")

        self.form_layout.addRow("Delay range (maximum delay that is reliably estimated):", self.double_spinbox_delayrange)

        self.setLayout(self.form_layout)

        self.double_spinbox_delayrange.valueChanged.connect(self.parent().set_delayrange)

    # method
    def saveState(self, settings):
        settings.setValue("delay_range", self.double_spinbox_delayrange.value())

    # method
    def restoreState(self, settings):
        delay_range = settings.value("delay_range", DEFAULT_DELAYRANGE, type=float)
        self.double_spinbox_delayrange.setValue(delay_range)
