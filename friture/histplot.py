#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth￩e Lecomte

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
from PyQt5 import QtWidgets
from PyQt5.QtQuickWidgets import QQuickWidget
from numpy import zeros, ones, log10
import numpy
from friture.filled_curve import CurveType, FilledCurve
from friture.histplot_data import HistPlot_Data
from friture.plotting.coordinateTransform import CoordinateTransform
import friture.plotting.frequency_scales as fscales
from friture.qml_tools import qml_url, raise_if_error
from friture.store import GetStore

# The peak decay rates (magic goes here :).
PEAK_DECAY_RATE = 1.0 - 3E-6

class HistPlot(QtWidgets.QWidget):

    def __init__(self, parent, engine):
        super(HistPlot, self).__init__(parent)

        self.logger = logging.getLogger(__name__)

        store = GetStore()
        self._histplot_data = HistPlot_Data(store)
        store._dock_states.append(self._histplot_data)
        state_id = len(store._dock_states) - 1

        self._curve_peak = FilledCurve(CurveType.PEEK)
        self._histplot_data.add_plot_item(self._curve_peak)

        self._curve_signal = FilledCurve(CurveType.SIGNAL)
        self._histplot_data.add_plot_item(self._curve_signal)

        self._histplot_data.show_legend = False
        self._histplot_data.vertical_axis.name = "PSD (dB A)"
        self._histplot_data.vertical_axis.setTrackerFormatter(lambda x: "%.1f dB" % (x))
        self._histplot_data.horizontal_axis.name = "Frequency (Hz)"
        self._histplot_data.horizontal_axis.setTrackerFormatter(self.format_frequency)

        self._histplot_data.vertical_axis.setRange(0, 1)
        self._histplot_data.horizontal_axis.setRange(44, 22000)

        self.paused = False

        self.peak = zeros((3,))
        self.peak_int = zeros((3,))
        self.peak_decay = ones((3,)) * PEAK_DECAY_RATE

        self.normVerticalScaleTransform = CoordinateTransform(0, 1, 1, 0, 0)
        self.normHorizontalScaleTransform = CoordinateTransform(44, 22000, 1, 0, 0)

        self.normHorizontalScaleTransform.setScale(fscales.Logarithmic)
        self._histplot_data.horizontal_axis.setScale(fscales.Logarithmic)

        plotLayout = QtWidgets.QGridLayout(self)
        plotLayout.setSpacing(0)
        plotLayout.setContentsMargins(0, 0, 0, 0)

        self.quickWidget = QQuickWidget(engine, self)
        self.quickWidget.statusChanged.connect(self.on_status_changed)
        self.quickWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.quickWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.quickWidget.setSource(qml_url("HistPlot.qml"))
        
        raise_if_error(self.quickWidget)

        self.quickWidget.rootObject().setProperty("stateId", state_id)

        plotLayout.addWidget(self.quickWidget)

        self.setLayout(plotLayout)

    def format_frequency(self, freq: float) -> str:
        return f'{freq:.0f} Hz ({fscales.freq_to_note(freq)})'

    def on_status_changed(self, status):
        if status == QQuickWidget.Error:
            for error in self.quickWidget.errors():
                self.logger.error("QML error: " + error.toString())

    def setdata(self, fl, fh, fc, y):
        if not self.paused:
            M = numpy.max(y)
            m = self.normVerticalScaleTransform.coord_min
            y_int = (y-m)/(numpy.abs(M-m)+1e-3)

            scaled_x_left = self.normHorizontalScaleTransform.toScreen(fl)
            scaled_x_right = self.normHorizontalScaleTransform.toScreen(fh)
            baseline = 1.
            scaled_y = 1. - self.normVerticalScaleTransform.toScreen(y)
            z = y_int

            self._curve_signal.setData(scaled_x_left, scaled_x_right, scaled_y, z, baseline)

            self.compute_peaks(y)
            scaled_peak = 1. - self.normVerticalScaleTransform.toScreen(self.peak)
            z_peak = self.peak_int
            self._curve_peak.setData(scaled_x_left, scaled_x_right, scaled_peak, z_peak, baseline)
            
            bar_label_x = (scaled_x_left + scaled_x_right)/2
            self._histplot_data.setBarLabels(bar_label_x, fc, scaled_y)

    def draw(self):
        return

    def pause(self):
        self.paused = True

    def restart(self):
        self.paused = False

    def canvasUpdate(self):
        return

    def compute_peaks(self, y):
        if len(self.peak) != len(y):
            y_ones = ones(y.shape)
            self.peak = y_ones * (-500.)
            self.peak_int = zeros(y.shape)
            self.peak_decay = y_ones * 20. * log10(PEAK_DECAY_RATE) * 5000

        mask1 = (self.peak < y)
        mask2 = (~mask1)
        mask2_a = mask2 * (self.peak_int < 0.2)
        mask2_b = mask2 * (self.peak_int >= 0.2)

        self.peak[mask1] = y[mask1]
        self.peak[mask2_a] = self.peak[mask2_a] + self.peak_decay[mask2_a]

        self.peak_decay[mask1] = 20. * log10(PEAK_DECAY_RATE) * 5000
        self.peak_decay[mask2_a] += 20. * log10(PEAK_DECAY_RATE) * 5000

        self.peak_int[mask1] = 1.
        self.peak_int[mask2_b] *= 0.975

    def setspecrange(self, spec_min, spec_max):
        if spec_min > spec_max:
            spec_min, spec_max = spec_max, spec_min

        self._histplot_data.vertical_axis.setRange(spec_min, spec_max)
        self.normVerticalScaleTransform.setRange(spec_min, spec_max)

    def setweighting(self, weighting):
        if weighting == 0:
            title = "PSD (dB)"
        elif weighting == 1:
            title = "PSD (dB A)"
        elif weighting == 2:
            title = "PSD (dB B)"
        else:
            title = "PSD (dB C)"

        self._histplot_data.vertical_axis.name = title
