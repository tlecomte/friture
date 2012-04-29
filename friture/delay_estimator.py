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
from friture.timeplot import TimePlot

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
SAMPLING_RATE = 44100

STYLESHEET = """
QwtPlotCanvas {
    border: 1px solid gray;
    border-radius: 2px;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
    stop: 0 #E0E0E0, stop: 0.5 #FFFFFF);
}
"""

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
        #self.PlotZoneUp = TimePlot(self, self.logger)
        #self.PlotZoneUp.setObjectName("PlotZoneUp")
        #self.gridLayout.addWidget(self.PlotZoneUp, 0, 0, 1, 1)
        self.delay_label = QtGui.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)
        self.delay_label.setFont(font)
        self.delay_label.setObjectName("delay_label")
        self.gridLayout.addWidget(self.delay_label, 0, 0, 1, 1)
        
        self.setStyleSheet(STYLESHEET)

        self.settings_dialog = Delay_Estimator_Settings_Dialog(self, self.logger)

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
        else:
            i0 = argmax(floatdata[0, :width]**2)
            t0_ms = float(i0)/SAMPLING_RATE*1e3 
            i1 = argmax(floatdata[1, i0:i0+width]**2) + i0 # only detect peaks that arrive later
            t1_ms = float(i1)/SAMPLING_RATE*1e3
            delay_ms = t1_ms - t0_ms
            #print i0, t0_ms, i1, t1_ms, delay_ms
            c = 340. # speed of sound, in meters per second (approximate)
            message = "%.1f ms\n (%.1f m)" %(delay_ms, delay_ms*1e-3*c)
            
            # detect overflow
            s0 = floatdata[0, i0]**2
            s1 = floatdata[1, i1]**2
            if s0==1. or s1==1.:
                message = "Overflow"

            # detect when the max is not clear enough ?
            m0 = (floatdata[0, :width]**2).mean()
            m1 = (floatdata[1, :width]**2).mean()
            #print s0, m0, s0/m0, s1, m1, s1/m1
            threshold = 100.
            if s0/m0 < threshold or s1/m1 < threshold:
                message = "Peak not found"

        if message <> self.previous_message:
            self.delay_label.setText(message)
            self.previous_message = message

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
