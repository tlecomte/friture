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

from PyQt4 import QtGui, QtCore
from numpy import argmax
import numpy
from numpy.fft import rfft, irfft
from filter import decimate
from friture import generated_filters
from ringbuffer import RingBuffer

from friture.audiobackend import SAMPLING_RATE

DEFAULT_DELAYRANGE = 1 # default delay range is 1 second

def subsampler(Ndec, bdec, adec, x, zis):      
    x_dec = x
    
    if zis == None:
        for i in range(Ndec):
            x_dec, zf = decimate(bdec, adec, x_dec)
        return x_dec, None
    else:
        m = 0
        zfs = []
        for i in range(Ndec):
            x_dec, zf = decimate(bdec, adec, x_dec, zi=zis[m])
            m += 1
            # zf can be reused to restart the filter
            zfs += [zf]
        return x_dec, zfs

# build a proper array of zero initial conditions to start the subsampler
def subsampler_filtic(Ndec, bdec, adec):
    zfs = []
    for i in range(Ndec):
        l = max(len(bdec), len(adec)) - 1
        zfs += [numpy.zeros(l)]
    return zfs    

class Delay_Estimator_Widget(QtGui.QWidget):
    def __init__(self, parent = None, logger = None):
        QtGui.QWidget.__init__(self, parent)

        self.audiobuffer = None
        
        # store the logger instance
        if logger is None:
            self.logger = parent.parent.logger
        else:
            self.logger = logger
        
        self.previous_delay_message = ""
        self.previous_correlation_message = ""
        self.previous_polarity_message = ""
        self.previous_channelInfo_message = ""
        
        self.setObjectName("Delay_Estimator_Widget")
        self.layout = QtGui.QFormLayout(self)
        self.layout.setObjectName("layout")
        
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)
        
        self.delay_label = QtGui.QLabel(self)
        self.delay_label.setFont(font)
        self.delay_label.setObjectName("delay_label")
        
        self.delayText_label = QtGui.QLabel(self)
        self.delayText_label.setObjectName("delayText_label")
        self.delayText_label.setText("Delay:")

        self.correlation_label = QtGui.QLabel(self)
        self.correlation_label.setObjectName("Correlation_label")
        
        self.correlationText_label = QtGui.QLabel(self)
        self.correlationText_label.setObjectName("correlationText_label")
        self.correlationText_label.setText("Correlation:")

        self.polarity_label = QtGui.QLabel(self)
        self.polarity_label.setFont(font)
        self.polarity_label.setObjectName("polarity_label")
        
        self.polarityText_label = QtGui.QLabel(self)
        self.polarityText_label.setObjectName("polarityText_label")
        self.polarityText_label.setText("Polarity:")
        
        self.channelInfo_label = QtGui.QLabel(self)
        self.channelInfo_label.setObjectName("channelInfo_label")
        
        self.layout.addRow(self.delayText_label, self.delay_label)
        self.layout.addRow(self.correlationText_label, self.correlation_label)
        self.layout.addRow(self.polarityText_label, self.polarity_label)
        self.layout.addRow(None, self.channelInfo_label)
        
        self.settings_dialog = Delay_Estimator_Settings_Dialog(self, self.logger)
        
        self.i = 0

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
        self.subsampled_sampling_rate = SAMPLING_RATE/2**(self.Ndec)
        [self.bdec, self.adec] = generated_filters.params['dec']
        self.zfs0 = subsampler_filtic(self.Ndec, self.bdec, self.adec)
        self.zfs1 = subsampler_filtic(self.Ndec, self.bdec, self.adec)

        # ringbuffers for the subsampled data        
        self.ringbuffer0 = RingBuffer()
        self.ringbuffer1 = RingBuffer()
        
        self.delayrange_s = DEFAULT_DELAYRANGE # confidence range
        
        self.old_Xcorr = None

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    # method
    def update(self):
        if not self.isVisible():
            return

        # temporary buffer just to check the data shape
        floatdata = self.audiobuffer.data(2)

        if floatdata.shape[0] == 1:
            message = """Delay estimator only works
with two channels.
Select two-channels mode
in the setup window."""
            if message <> self.previous_channelInfo_message:
                self.previous_delay_message = "N/A ms\n(N/A m)"
                self.delay_label.setText(self.previous_delay_message)
                self.previous_correlation_message = "N/A %"
                self.correlation_label.setText(self.previous_correlation_message)
                self.previous_polarity_message = "N/A"
                self.polarity_label.setText(self.previous_polarity_message)
                self.channelInfo_label.setText(message)
                self.previous_channelInfo_message = message
        else:
            #get the fresh data
            floatdata = self.audiobuffer.newdata()
            # separate the channels
            x0 = floatdata[0,:]
            x1 = floatdata[1,:]
            #subsample them
            x0_dec, self.zfs0 = subsampler(self.Ndec, self.bdec, self.adec, x0, self.zfs0)
            x1_dec, self.zfs1 = subsampler(self.Ndec, self.bdec, self.adec, x1, self.zfs1)
            # push to a 1-second ring buffer
            x0_dec.shape = (1, x0_dec.size)
            x1_dec.shape = (1, x1_dec.size)
            self.ringbuffer0.push(x0_dec)
            self.ringbuffer1.push(x1_dec)

            if (self.i==5):
                self.i = 0
                # retrieve last one-second of data
                time = 2*self.delayrange_s
                length = time*self.subsampled_sampling_rate
                d0 = self.ringbuffer0.data(length)
                d1 = self.ringbuffer1.data(length)
                d0.shape = (d0.size)
                d1.shape = (d1.size)
                std0 = numpy.std(d0)
                std1 = numpy.std(d1)
                if d0.size>0 and std0>0. and std1>0.:
                    # substract the means
                    # (in order to get a normalized cross-correlation at the end)
                    d0 -= d0.mean()
                    d1 -= d1.mean()
                    # compute the cross-correlation
                    D0 = rfft(d0)
                    D1 = rfft(d1)
                    D0r = D0.conjugate()
                    G = D0r*D1
                    G = (G==0.)*1e-30 + (G<>0.)*G
                    #W = 1. # frequency unweighted
                    W = 1./numpy.abs(G) # "PHAT"
                    #D1r = D1.conjugate(); G0 = D0r*D0; G1 = D1r*D1; W = numpy.abs(G)/(G0*G1) # HB weighted
                    Xcorr = irfft(W*G)
                    #Xcorr_unweighted = irfft(G)
                    #numpy.save("d0.npy", d0)
                    #numpy.save("d1.npy", d1)
                    #numpy.save("Xcorr.npy", Xcorr)

                    if self.old_Xcorr != None and self.old_Xcorr.shape == Xcorr.shape:
                        # smoothing
                        alpha = 0.2
                        Xcorr = alpha*Xcorr + (1. - alpha)*self.old_Xcorr
                    
                    absXcorr = numpy.abs(Xcorr)
                    i = argmax(absXcorr)
                    # normalize
                    #Xcorr_max_norm = Xcorr_unweighted[i]/(d0.size*std0*std1)
                    Xcorr_extremum = Xcorr[i]
                    Xcorr_max_norm = abs(Xcorr[i])/(3*numpy.std(Xcorr))
                    delay_ms = 1e3*float(i)/self.subsampled_sampling_rate
                
                    # store for smoothing
                    self.old_Xcorr = Xcorr
                else:
                    delay_ms = 0.
                    Xcorr_max_norm = 0.
                    Xcorr_extremum = 0.

                # debug wrong phase detection
                #if Xcorr[i] < 0.:
                #    numpy.save("Xcorr.npy", Xcorr)

                c = 340. # speed of sound, in meters per second (approximate)
                distance_m = delay_ms*1e-3*c

                # home-made measure of the significance
                slope = 0.12
                p = 3
                x = (Xcorr_max_norm>1.)*(Xcorr_max_norm-1.)
                x = (slope*x)**p
                correlation = int((x/(1. + x))*100)
                
                delay_message = "%.1f ms\n(%.2f m)" %(delay_ms, distance_m)
                correlation_message = "%d%%" %(correlation)
                if Xcorr_extremum >= 0:
                    polarity_message = "In-phase"
                else:
                    polarity_message = "Reversed phase"                
                channelInfo_message = ""

                if delay_message <> self.previous_delay_message:
                    self.delay_label.setText(delay_message)
                    self.previous_delay_message = delay_message
                if correlation_message <> self.previous_correlation_message:
                    self.correlation_label.setText(correlation_message)
                    self.previous_correlation_message = correlation_message
                if polarity_message <> self.previous_polarity_message:
                    self.polarity_label.setText(polarity_message)
                    self.previous_polarity_message = polarity_message
                if channelInfo_message <> self.previous_channelInfo_message:
                    self.channelInfo_label.setText(channelInfo_message)
                    self.previous_channelInfo_message = channelInfo_message


            self.i += 1
    
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

class Delay_Estimator_Settings_Dialog(QtGui.QDialog):
    def __init__(self, parent, logger):
        QtGui.QDialog.__init__(self, parent)
        
        self.parent = parent
        self.logger = logger
        
        self.setWindowTitle("Delay estimator settings")
        
        self.formLayout = QtGui.QFormLayout(self)
        
        self.doubleSpinBox_delayrange = QtGui.QDoubleSpinBox(self)
        self.doubleSpinBox_delayrange.setDecimals(1)
        self.doubleSpinBox_delayrange.setMinimum(0.1)
        self.doubleSpinBox_delayrange.setMaximum(1000.0)
        self.doubleSpinBox_delayrange.setProperty("value", DEFAULT_DELAYRANGE)
        self.doubleSpinBox_delayrange.setObjectName("doubleSpinBox_delayrange")
        self.doubleSpinBox_delayrange.setSuffix(" s")

        self.formLayout.addRow("Delay range (maximum delay that is reliably estimated):", self.doubleSpinBox_delayrange)
        
        self.setLayout(self.formLayout)
        
        self.connect(self.doubleSpinBox_delayrange, QtCore.SIGNAL('valueChanged(double)'), self.parent.set_delayrange)

    # method
    def saveState(self, settings):
        settings.setValue("delayRange", self.doubleSpinBox_delayrange.value())

    # method
    def restoreState(self, settings):
        (delayRange, ok) = settings.value("delayRange", DEFAULT_DELAYRANGE).toDouble()
        self.doubleSpinBox_delayrange.setValue(delayRange)
