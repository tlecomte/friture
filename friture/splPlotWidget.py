#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
import logging

from PyQt5 import QtWidgets
from PyQt5.QtQuickWidgets import QQuickWidget

from numpy import zeros, ones, log10
import numpy as np

from friture.audiobackend import SAMPLING_RATE
from friture.plotting.coordinateTransform import CoordinateTransform
from friture.spl_data import SPLData
from friture.filled_curve import CurveType, FilledCurve
from friture.pitch_tracker import format_frequency
from friture.store import GetStore
from friture.qml_tools import qml_url, raise_if_error

# The peak decay rates (magic goes here :).
PEAK_DECAY_RATE = 1.0 - 3e-6
# Number of cycles the peak stays on hold before fall-off.
PEAK_FALLOFF_COUNT = 32  # default : 16


class Baseline(Enum):
    PLOT_BOTTOM = (1,)
    DATA_ZERO = 2


class SPLPlotWidget(QtWidgets.QWidget):

    def __init__(self, parent, engine):
        super(SPLPlotWidget, self).__init__(parent)

        self.logger = logging.getLogger(__name__)

        store = GetStore()
        self._SPLData = SPLData(store)
        store._dock_states.append(self._SPLData)
        state_id = len(store._dock_states) - 1

        self._curve_signal = FilledCurve(CurveType.SIGNAL)
        self._SPLData.add_plot_item(self._curve_signal)

        self._curve_peak = FilledCurve(CurveType.PEEK)

        self._SPLData.show_legend = False
        self._SPLData.vertical_axis.name = "SPL (dB)"
        self._SPLData.vertical_axis.setTrackerFormatter(lambda x: "%.1f dB" % (x))
        self._SPLData.horizontal_axis.name = "Frequency (Hz)"
        self._SPLData.horizontal_axis.setTrackerFormatter(format_frequency)
        self._SPLData.horizontal_axis.show_minor_grid_lines = True

        self._SPLData.vertical_axis.setRange(0, 1)
        self._SPLData.horizontal_axis.setRange(0, 22000)

        self._baseline = Baseline.PLOT_BOTTOM

        self.paused = False

        self.peaks_enabled = True
        self.peak = zeros((3,))
        self.peak_int = zeros((3,))
        self.peak_decay = ones((3,)) * PEAK_DECAY_RATE

        self.normVerticalScaleTransform = CoordinateTransform(0, 1, 1, 0, 0)
        self.normHorizontalScaleTransform = CoordinateTransform(0, 22000, 1, 0, 0)

        plotLayout = QtWidgets.QGridLayout(self)
        plotLayout.setSpacing(0)
        plotLayout.setContentsMargins(0, 0, 0, 0)

        self.quickWidget = QQuickWidget(engine, self)
        self.quickWidget.statusChanged.connect(self.on_status_changed)
        self.quickWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.quickWidget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.quickWidget.setSource(qml_url("SPL.qml"))

        raise_if_error(self.quickWidget)

        self.quickWidget.rootObject().setProperty("stateId", state_id)

        plotLayout.addWidget(self.quickWidget)

        self.setLayout(plotLayout)

    def on_status_changed(self, status):
        if status == QQuickWidget.Error:
            for error in self.quickWidget.errors():
                self.logger.error("QML error: " + error.toString())

    def setfreqscale(self, scale):
        self.normHorizontalScaleTransform.setScale(scale)
        self._SPLData.horizontal_axis.setScale(scale)

    def setfreqrange(self, minfreq, maxfreq):
        self.xmin = minfreq
        self.xmax = maxfreq

        self._SPLData.horizontal_axis.setRange(minfreq, maxfreq)
        self.normHorizontalScaleTransform.setRange(minfreq, maxfreq)

    def setspecrange(self, spec_min, spec_max):
        if spec_min > spec_max:
            spec_min, spec_max = spec_max, spec_min

        self._SPLData.vertical_axis.setRange(spec_min, spec_max)
        self.normVerticalScaleTransform.setRange(spec_min, spec_max)

    def setweighting(self, weighting):
        if weighting == 0:
            title = "SPL (dB A)"
        elif weighting == 1:
            title = "SPL (dB B)"
        else:
            title = "SPL (dB C)"

        self._SPLData.vertical_axis.name = title

    def setShowFreqLabel(self, showFreqLabel):
        self._SPLData.showFrequencyTracker = showFreqLabel

    def setShowPitchLabel(self, showPitchLabel):
        self._SPLData.showPitchTracker = showPitchLabel

    def set_peaks_enabled(self, enabled):
        self.peaks_enabled = enabled

        if enabled:
            self._SPLData.insert_plot_item(0, self._curve_peak)
        else:
            self._SPLData.remove_plot_item(self._curve_peak)

    def set_baseline_displayUnits(self, baseline):
        self._baseline = Baseline.PLOT_BOTTOM

    def set_baseline_dataUnits(self, baseline):
        self._baseline = Baseline.DATA_ZERO

    def setdata(self, x, y, fmax, fpitch):
        if not self.paused:
            if fmax < 2e2:
                text = "%.1f Hz" % (fmax)
            else:
                text = "%d Hz" % (np.rint(fmax))
            self._SPLData.setFmax(
                text, self.normHorizontalScaleTransform.toScreen(fmax)
            )
            self._SPLData.setFpitch(
                format_frequency(fpitch),
                self.normHorizontalScaleTransform.toScreen(fpitch),
            )

            M = np.max(y)
            m = self.normVerticalScaleTransform.coord_min
            y_int = (y - m) / (np.abs(M - m) + 1e-3)

            x_left = zeros(x.shape)
            x_right = zeros(x.shape)
            x_left[0] = 1e-10
            x_left[1:] = (x[1:] + x[:-1]) / 2.0
            x_right[:-1] = x_left[1:]
            x_right[-1] = float(SAMPLING_RATE / 2)
            scaled_x_left = self.normHorizontalScaleTransform.toScreen(x_left)
            scaled_x_right = self.normHorizontalScaleTransform.toScreen(x_right)

            baseline = (
                1.0
                if self._baseline == Baseline.PLOT_BOTTOM
                else (1.0 - self.normVerticalScaleTransform.toScreen(0.0))
            )

            scaled_y = 1.0 - self.normVerticalScaleTransform.toScreen(y)
            z = y_int
            self._curve_signal.setData(
                scaled_x_left, scaled_x_right, scaled_y, z, baseline
            )

            if self.peaks_enabled:
                self.compute_peaks(y)
                scaled_peak = 1.0 - self.normVerticalScaleTransform.toScreen(self.peak)
                z_peak = self.peak_int
                self._curve_peak.setData(
                    scaled_x_left, scaled_x_right, scaled_peak, z_peak, baseline
                )

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
            self.peak = y_ones * (-500.0)
            self.peak_int = zeros(y.shape)
            self.peak_decay = y_ones * 20.0 * log10(PEAK_DECAY_RATE) * 5000

        mask1 = self.peak < y
        mask2 = ~mask1
        mask2_a = mask2 * (self.peak_int < 0.2)
        mask2_b = mask2 * (self.peak_int >= 0.2)

        self.peak[mask1] = y[mask1]
        self.peak[mask2_a] = self.peak[mask2_a] + self.peak_decay[mask2_a]

        self.peak_decay[mask1] = 20.0 * log10(PEAK_DECAY_RATE) * 5000
        self.peak_decay[mask2_a] += 20.0 * log10(PEAK_DECAY_RATE) * 5000

        self.peak_int[mask1] = 1.0
        self.peak_int[mask2_b] *= 0.975
