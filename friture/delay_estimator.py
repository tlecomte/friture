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

from PyQt4 import QtGui
from numpy import argmax
import numpy
from numpy.fft import rfft, irfft
from filter import decimate
from friture import generated_filters
from ringbuffer import RingBuffer

SAMPLING_RATE = 44100

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
        
        self.previous_message = ""
        
        self.setObjectName("Delay_Estimattor_Widget")
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.delay_label = QtGui.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)
        self.delay_label.setFont(font)
        self.delay_label.setObjectName("delay_label")
        self.gridLayout.addWidget(self.delay_label, 0, 0, 1, 1)
        
        self.settings_dialog = Delay_Estimator_Settings_Dialog(self, self.logger)
        
        self.i = 0

        # We will decimate several times
        # no decimation => 1/fs = 23 µs resolution
        # 1 ms resolution => fs = 1000 Hz is enough => can divide the sampling rate by 44 !
        # if I decimate 2 times (2**2 = 4 => 0.092 ms (3 cm) resolution)!
        # if I decimate 3 times (2**3 = 8 => 0.184 ms (6 cm) resolution)!
        # if I decimate 5 times (2**5 = 32 => 0.7 ms (24 cm) resolution)!
        # (actually, I could fit a gaussian on the cross-correlation peak to get
        # higher resolution even at low sample rates)
        self.Ndec = 3
        self.subsampled_sampling_rate = SAMPLING_RATE/2**(self.Ndec)
        [self.bdec, self.adec] = generated_filters.params['dec']
        self.zfs = subsampler_filtic(self.Ndec, self.bdec, self.adec)

        # ringbuffers for the subsampled data        
        self.ringbuffer0 = RingBuffer()
        self.ringbuffer1 = RingBuffer()

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    # method
    def update(self):
        if not self.isVisible():
            return

        time = 1.
        width = time*SAMPLING_RATE
        floatdata = self.audiobuffer.data(2*width)

        if floatdata.shape[0] == 1:
            message = """Delay estimator only works
with two channels.
Select two-channels mode
in the setup window."""
            if message <> self.previous_message:
                self.delay_label.setText(message)
                self.previous_message = message
        else:
            #get the fresh data
            floatdata = self.audiobuffer.newdata()
            # separate the channels
            x0 = floatdata[0,:]
            x1 = floatdata[1,:]
            #subsample them
            x0_dec, self.zfs = subsampler(self.Ndec, self.bdec, self.adec, x0, self.zfs)
            x1_dec, self.zfs = subsampler(self.Ndec, self.bdec, self.adec, x1, self.zfs)
            # push to a 1-second ring buffer
            x0_dec.shape = (1, x0_dec.size)
            x1_dec.shape = (1, x1_dec.size)
            self.ringbuffer0.push(x0_dec)
            self.ringbuffer1.push(x1_dec)

            if (self.i==10):
                self.i = 0
                # retrieve last one-second of data
                time = 2.
                length = time*self.subsampled_sampling_rate
                d0 = self.ringbuffer0.data(length)
                d1 = self.ringbuffer1.data(length)
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
                    D0r = D0.conjugate() # FIXME D0r was supposed to be -D0.conjugate(), not +D0.conjugate()
                    Xcorr = irfft(D0r*D1)
                    #numpy.save("Xcorr.npy", Xcorr)
                    absXcorr = numpy.abs(Xcorr)
                    i = argmax(absXcorr)
                    # normalize
                    Xcorr_max_norm = Xcorr[0,i]/(d0.size*std0*std1)
                    delay_ms = 1e3*float(i)/self.subsampled_sampling_rate
                else:
                    delay_ms = 0.
                    Xcorr_max_norm = 0.

                c = 340. # speed of sound, in meters per second (approximate)
                distance_m = delay_ms*1e-3*c

                certainty = int(abs(Xcorr_max_norm)*100)                
                
                if Xcorr_max_norm >= 0:
                    phase_message = "In-phase"
                else:
                    phase_message = "Reversed phase"
                
                message = "%.1f ms\n(%.2f m)\n\nCertainty %d%%\n\n%s" %(delay_ms, distance_m, certainty, phase_message)

                if message <> self.previous_message:
                    self.delay_label.setText(message)
                    self.previous_message = message

            self.i += 1
    
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
        
        #self.doubleSpinBox_timerange = QtGui.QDoubleSpinBox(self)
        #self.doubleSpinBox_timerange.setDecimals(1)
        #self.doubleSpinBox_timerange.setMinimum(0.1)
        #self.doubleSpinBox_timerange.setMaximum(1000.0)
        #self.doubleSpinBox_timerange.setProperty("value", DEFAULT_TIMERANGE)
        #self.doubleSpinBox_timerange.setObjectName("doubleSpinBox_timerange")
        #self.doubleSpinBox_timerange.setSuffix(" s")

        #self.formLayout.addRow("Time range:", self.doubleSpinBox_timerange)
        self.formLayout.addRow("No settings for the delay estimator.", None)
        
        self.setLayout(self.formLayout)

        #self.connect(self.doubleSpinBox_timerange, QtCore.SIGNAL('valueChanged(double)'), self.parent.timerangechanged)

    # method
    def saveState(self, settings):
        #settings.setValue("timeRange", self.doubleSpinBox_timerange.value())
        return

    # method
    def restoreState(self, settings):
        #(timeRange, ok) = settings.value("timeRange", DEFAULT_TIMERANGE).toDouble()
        #self.doubleSpinBox_timerange.setValue(timeRange)
        return
