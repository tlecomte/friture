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
from numpy import log10, where, linspace, sign, arange
from friture.timeplot import TimePlot
from friture.audiobackend import SAMPLING_RATE
from friture.logger import PrintLogger

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
DEFAULT_TIMERANGE = 2*SMOOTH_DISPLAY_TIMER_PERIOD_MS

class Scope_Widget(QtGui.QWidget):
    def __init__(self, parent, sharedGLWidget, logger = PrintLogger()):
        QtGui.QWidget.__init__(self, parent)

        self.audiobuffer = None
        self.logger = logger
        
        self.setObjectName("Scope_Widget")
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneUp = TimePlot(self, sharedGLWidget, self.logger)
        self.PlotZoneUp.setObjectName("PlotZoneUp")
        self.gridLayout.addWidget(self.PlotZoneUp, 0, 0, 1, 1)

        self.settings_dialog = Scope_Settings_Dialog(self, self.logger)

        self.timerange = DEFAULT_TIMERANGE

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    # method
    def update(self):
        if not self.isVisible():
            return

        time = self.timerange*1e-3
        width = int(time*SAMPLING_RATE)
        #basic trigger capability on leading edge
        floatdata = self.audiobuffer.data(2*width)

        #number of data points received at the last audio buffer update
        #newpoints = self.audiobuffer.newpoints
        #print newpoints

        # because of the buffering, sometimes we have not got any data
        #if newpoints==0:
        #    return
        
        #floatdata = self.audiobuffer.data(newpoints + width)

        twoChannels = False
        if floatdata.shape[0] > 1:
            twoChannels = True

        # trigger on the first channel only
        triggerdata = floatdata[0,:]
        # trigger on half of the waveform
        trig_search_start = width/2
        trig_search_stop = -width/2
        triggerdata = triggerdata[trig_search_start : trig_search_stop]

        max = floatdata.max()
        trigger_level = max*2./3.
        #trigger_level = 0.6
        trigger_pos = where((triggerdata[:-1] < trigger_level)*(triggerdata[1:] >= trigger_level))[0]

        if len(trigger_pos)==0:
            return
        
        if len(trigger_pos) > 0:
            shift = trigger_pos[0]
        else:
            #return
            shift = 0
        shift += trig_search_start
        datarange = width
        floatdata = floatdata[:, shift -  datarange/2: shift +  datarange/2]
 
        y = floatdata[0,:] #- floatdata.mean()
        if twoChannels:
            y2 = floatdata[1,:] #- floatdata.mean()
        
        dBscope = False
        if dBscope:
            dBmin = -50.
            y = sign(y)*(20*log10(abs(y))).clip(dBmin, 0.)/(-dBmin) + sign(y)*1.
            if twoChannels:
                y2 = sign(y2)*(20*log10(abs(y2))).clip(dBmin, 0.)/(-dBmin) + sign(y2)*1.
    
        time = (arange(len(y)) - datarange/2)/float(SAMPLING_RATE)
        
        if twoChannels:
            self.PlotZoneUp.setdataTwoChannels(time, y, y2)
        else:
            self.PlotZoneUp.setdata(time, y)

    # slot
    def set_timerange(self, timerange):
        self.timerange = timerange

    # slot
    def settings_called(self, checked):
        self.settings_dialog.show()

    # method
    def saveState(self, settings):
        self.settings_dialog.saveState(settings)
    
    # method
    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)


class Scope_Settings_Dialog(QtGui.QDialog):
    def __init__(self, parent, logger):
        QtGui.QDialog.__init__(self, parent)
        
        self.logger = logger
        
        self.setWindowTitle("Scope settings")
        
        self.formLayout = QtGui.QFormLayout(self)
        
        self.doubleSpinBox_timerange = QtGui.QDoubleSpinBox(self)
        self.doubleSpinBox_timerange.setDecimals(1)
        self.doubleSpinBox_timerange.setMinimum(0.1)
        self.doubleSpinBox_timerange.setMaximum(1000.0)
        self.doubleSpinBox_timerange.setProperty("value", DEFAULT_TIMERANGE)
        self.doubleSpinBox_timerange.setObjectName("doubleSpinBox_timerange")
        self.doubleSpinBox_timerange.setSuffix(" ms")

        self.formLayout.addRow("Time range:", self.doubleSpinBox_timerange)
        
        self.setLayout(self.formLayout)

        self.connect(self.doubleSpinBox_timerange, QtCore.SIGNAL('valueChanged(double)'), self.parent().set_timerange)

    # method
    def saveState(self, settings):
        settings.setValue("timeRange", self.doubleSpinBox_timerange.value())

    # method
    def restoreState(self, settings):
        timeRange = float(settings.value("timeRange", DEFAULT_TIMERANGE))
        self.doubleSpinBox_timerange.setValue(timeRange)
