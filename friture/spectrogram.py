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
from numpy import log10, where, linspace
from friture.imageplot import ImagePlot
from friture.audioproc import audioproc # audio processing class
from friture.spectrogram_settings import Spectrogram_Settings_Dialog# settings dialog

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
SAMPLING_RATE = 44100

# shared with spectrogram_settings.py
DEFAULT_FFT_SIZE = 7 #4096 points
DEFAULT_FREQ_SCALE = 1 #log10
DEFAULT_MAXFREQ = SAMPLING_RATE/2
DEFAULT_MINFREQ = 20
DEFAULT_SPEC_MIN = -140
DEFAULT_SPEC_MAX = 0
DEFAULT_TIMERANGE = 10.
DEFAULT_WEIGHTING = 1 #A

class Spectrogram_Widget(QtGui.QWidget):
    def __init__(self, parent, logger = None):
        QtGui.QWidget.__init__(self, parent)

        # store the logger instance
        if logger is None:
            self.logger = parent.parent().logger
        else:
            self.logger = logger
        
        self.parent = parent

        self.setObjectName("Spectrogram_Widget")
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneImage = ImagePlot(self, self.logger)
        self.PlotZoneImage.setObjectName("PlotZoneImage")
        self.gridLayout.addWidget(self.PlotZoneImage, 0, 1, 1, 1)

        self.audiobuffer = None
        
        # initialize the class instance that will do the fft
        self.proc = audioproc(self.logger)

        self.maxfreq = DEFAULT_MAXFREQ
        self.minfreq = DEFAULT_MINFREQ
        self.fft_size = 2**DEFAULT_FFT_SIZE*32
        self.spec_min = DEFAULT_SPEC_MIN
        self.spec_max = DEFAULT_SPEC_MAX
        self.weighting = DEFAULT_WEIGHTING
        
        self.spectrogram_timer_time = 0.
        
        self.timerange_s = DEFAULT_TIMERANGE
        self.canvas_width = 100.
        
        self.PlotZoneImage.setlog10freqscale() #DEFAULT_FREQ_SCALE = 1 #log10
        self.PlotZoneImage.setfreqrange(self.minfreq, self.maxfreq)
        self.PlotZoneImage.setspecrange(self.spec_min, self.spec_max)
        self.PlotZoneImage.setweighting(self.weighting)
        self.PlotZoneImage.settimerange(self.timerange_s)
        
        # this timer is used to update the spectrogram widget, whose update period
        # is fixed by the time scale and the width of the widget canvas
        self.timer = QtCore.QTimer()
        self.period_ms = SMOOTH_DISPLAY_TIMER_PERIOD_MS
        self.timer.setInterval(self.period_ms) # variable timing
        
        # initialize the settings dialog
        self.settings_dialog = Spectrogram_Settings_Dialog(self, self.logger)
        
        # timer ticks
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.timer_slot)
        
        # window resize
        self.connect(self.PlotZoneImage.plotImage.canvasscaledspectrogram, QtCore.SIGNAL("canvasWidthChanged"), self.canvasWidthChanged)

        # we do not use the display timer since we have a special one
        # tell the caller by setting this variable as None
        self.update = None
  
        self.timer_time = QtCore.QTime()
  
 # FIXME
 # for smoothness, the following shoudl be observed
 # - the FFT should be done with Hamming, or Hanning or Kaiser windows
 #   with 50% or more overlap.
 # - the animation should be advanced according to the actual time elapsed
 #   since the last update. Proper advancement is done through interpolation.
 #   (Linear or quadratic (causal!) interpolation should be fine first)
 # - ideally timer should be removed altogether and replaced by bloacking OpenGL
 #   paintings synchronized to vsync

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    # method
    def custom_update(self):
        if not self.isVisible():
            return
        
        # FIXME We should allow here for more intelligent transforms, especially when the log freq scale is selected
        floatdata = self.audiobuffer.data(self.fft_size)

        # for now, take the first channel only
        floatdata = floatdata[0,:]

        sp, freq, A, B, C = self.proc.analyzelive(floatdata, self.fft_size, self.maxfreq)
        # scale the db spectrum from [- spec_range db ... 0 db] > [0..1]
        epsilon = 1e-30
        
        if self.weighting is 0:
            w = 0.
        elif self.weighting is 1:
            w = A
        elif self.weighting is 2:
            w = B
        else:
            w = C
        
        db_spectrogram = 20*log10(sp + epsilon) + w
        norm_spectrogram = (db_spectrogram.clip(min = self.spec_min, max = self.spec_max) - self.spec_min)/(self.spec_max - self.spec_min)
        
        self.PlotZoneImage.addData(freq, norm_spectrogram)

    def setminfreq(self, freq):
        self.minfreq = freq
        self.PlotZoneImage.setfreqrange(self.minfreq, self.maxfreq)

    def setmaxfreq(self, freq):
        self.maxfreq = freq
        self.PlotZoneImage.setfreqrange(self.minfreq, self.maxfreq)
    
    def setfftsize(self, fft_size):
        self.fft_size = fft_size

    def setmin(self, value):
        self.spec_min = value
        self.PlotZoneImage.setspecrange(self.spec_min, self.spec_max)
    
    def setmax(self, value):
        self.spec_max = value
        self.PlotZoneImage.setspecrange(self.spec_min, self.spec_max)
    
    def setweighting(self, weighting):
        self.weighting = weighting
        self.PlotZoneImage.setweighting(weighting)
    
    def settings_called(self, checked):
        self.settings_dialog.show()
    
    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)

    # slot
    def timerangechanged(self, value):
        self.timerange_s = value
        self.PlotZoneImage.settimerange(value)
        self.reset_timer()

    # slot
    def canvasWidthChanged(self, width):
        self.canvas_width = width
        self.reset_timer()

    # method
    def reset_timer(self):
        # FIXME millisecond resolution is limiting !
        # need to find a way to integrate this cleverly in the GUI
        # When the period is smaller than 25 ms, we can reasonably
        # try to draw as many columns at once as possible
        self.period_ms = 1000.*self.timerange_s/self.canvas_width
        self.logger.push("Resetting the timer, will fire every %d ms" %(self.period_ms))
        self.timer.setInterval(self.period_ms)
        
    # slot
    def timer_slot(self):
        #(chunks, t) = self.audiobuffer.update(self.audiobackend.stream)
        #self.chunk_number += chunks
        #self.buffer_timer_time = (95.*self.buffer_timer_time + 5.*t)/100.

        t = QtCore.QTime()
        t.start()

        self.custom_update()
        
        self.spectrogram_timer_time = (95.*self.spectrogram_timer_time + 5.*t.elapsed())/100.

        # Achieved timer period can be much higher than the one
        # we asked for, and is very variable
        # => We cannot rely on it
        # print "asked for:", self.period_ms, "achieved:", self.timer_time.restart()
