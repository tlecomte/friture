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

from PyQt5 import QtWidgets
from numpy import log10, where, sign, arange, zeros
from friture.timeplot import TimePlot
from friture.audiobackend import SAMPLING_RATE

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
DEFAULT_TIMERANGE = 2 * SMOOTH_DISPLAY_TIMER_PERIOD_MS


class Scope_Widget(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.audiobuffer = None

        self.setObjectName("Scope_Widget")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneUp = TimePlot(self)
        self.PlotZoneUp.setObjectName("PlotZoneUp")
        self.gridLayout.addWidget(self.PlotZoneUp, 0, 0, 1, 1)

        self.settings_dialog = Scope_Settings_Dialog(self)

        self.timerange = DEFAULT_TIMERANGE

        self.time = zeros(10)
        self.y = zeros(10)
        self.y2 = zeros(10)

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata):
        time = self.timerange * 1e-3
        width = int(time * SAMPLING_RATE)
        # basic trigger capability on leading edge
        floatdata = self.audiobuffer.data(2 * width)

        twoChannels = False
        if floatdata.shape[0] > 1:
            twoChannels = True

        # trigger on the first channel only
        triggerdata = floatdata[0, :]
        # trigger on half of the waveform
        trig_search_start = width // 2
        trig_search_stop = -width // 2
        triggerdata = triggerdata[trig_search_start: trig_search_stop]

        trigger_level = floatdata.max() * 2. / 3.
        trigger_pos = where((triggerdata[:-1] < trigger_level) * (triggerdata[1:] >= trigger_level))[0]

        if len(trigger_pos) == 0:
            return

        if len(trigger_pos) > 0:
            shift = trigger_pos[0]
        else:
            shift = 0
        shift += trig_search_start
        datarange = width
        floatdata = floatdata[:, shift - datarange // 2: shift + datarange // 2]

        self.y = floatdata[0, :]
        if twoChannels:
            self.y2 = floatdata[1, :]
        else:
            self.y2 = None

        dBscope = False
        if dBscope:
            dBmin = -50.
            self.y = sign(self.y) * (20 * log10(abs(self.y))).clip(dBmin, 0.) / (-dBmin) + sign(self.y) * 1.
            if twoChannels:
                self.y2 = sign(self.y2) * (20 * log10(abs(self.y2))).clip(dBmin, 0.) / (-dBmin) + sign(self.y2) * 1.
            else:
                self.y2 = None

        self.time = (arange(len(self.y)) - datarange // 2) / float(SAMPLING_RATE)

        if self.y2 is not None:
            self.PlotZoneUp.setdataTwoChannels(self.time*1e3, self.y, self.y2)
        else:
            self.PlotZoneUp.setdata(self.time*1e3, self.y)

    # method
    def canvasUpdate(self):
        return

    def pause(self):
        self.PlotZoneUp.pause()

    def restart(self):
        self.PlotZoneUp.restart()

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


class Scope_Settings_Dialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Scope settings")

        self.formLayout = QtWidgets.QFormLayout(self)

        self.doubleSpinBox_timerange = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_timerange.setDecimals(1)
        self.doubleSpinBox_timerange.setMinimum(0.1)
        self.doubleSpinBox_timerange.setMaximum(1000.0)
        self.doubleSpinBox_timerange.setProperty("value", DEFAULT_TIMERANGE)
        self.doubleSpinBox_timerange.setObjectName("doubleSpinBox_timerange")
        self.doubleSpinBox_timerange.setSuffix(" ms")

        self.formLayout.addRow("Time range:", self.doubleSpinBox_timerange)

        self.setLayout(self.formLayout)

        self.doubleSpinBox_timerange.valueChanged.connect(self.parent().set_timerange)

    # method
    def saveState(self, settings):
        settings.setValue("timeRange", self.doubleSpinBox_timerange.value())

    # method
    def restoreState(self, settings):
        timeRange = settings.value("timeRange", DEFAULT_TIMERANGE, type=float)
        self.doubleSpinBox_timerange.setValue(timeRange)
