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

from PyQt5 import Qt, QtWidgets
from numpy import zeros, ones, log10, array
from friture.histogramitem import HistogramItem
from friture.histplotpeakbaritem import HistogramPeakBarItem
from friture.plotting.scaleWidget import VerticalScaleWidget, HorizontalScaleWidget
from friture.plotting.scaleDivision import ScaleDivision
from friture.plotting.coordinateTransform import CoordinateTransform
from friture.plotting.canvasWidget import CanvasWidget
import friture.plotting.frequency_scales as fscales

# The peak decay rates (magic goes here :).
PEAK_DECAY_RATE = 1.0 - 3E-6

class HistPlot(QtWidgets.QWidget):

    def __init__(self, parent):
        super(HistPlot, self).__init__()

        self.verticalScaleDivision = ScaleDivision(-140, 0)
        self.verticalScaleTransform = CoordinateTransform(-140, 0, 100, 0, 0)

        self.verticalScale = VerticalScaleWidget(self, self.verticalScaleDivision, self.verticalScaleTransform)
        self.verticalScale.setTitle("PSD (dB A)")

        self.horizontalScaleDivision = ScaleDivision(44, 22000)
        self.horizontalScaleTransform = CoordinateTransform(44, 22000, 100, 0, 0)

        self.horizontalScale = HorizontalScaleWidget(self, self.horizontalScaleDivision, self.horizontalScaleTransform)
        self.horizontalScale.setTitle("Frequency (Hz)")

        self.canvasWidget = CanvasWidget(self, self.verticalScaleTransform, self.horizontalScaleTransform)
        self.canvasWidget.setTrackerFormatter(lambda x, y: "%d Hz, %.1f dB" % (x, y))

        plot_layout = QtWidgets.QGridLayout()
        plot_layout.setSpacing(0)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.addWidget(self.verticalScale, 0, 0)
        plot_layout.addWidget(self.canvasWidget, 0, 1)
        plot_layout.addWidget(self.horizontalScale, 1, 1)

        self.setLayout(plot_layout)

        self.needfullreplot = False

        self.horizontalScaleTransform.setScale(fscales.Logarithmic)
        self.horizontalScaleDivision.setScale(fscales.Logarithmic)

        # insert an additional plot item for the peak bar
        self.bar_peak = HistogramPeakBarItem()
        self.canvasWidget.attach(self.bar_peak)
        self.peak = zeros((1,))
        self.peak_int = 0
        self.peak_decay = PEAK_DECAY_RATE

        self.histogram = HistogramItem()
        self.histogram.set_color(Qt.Qt.darkGreen)
        self.canvasWidget.attach(self.histogram)

        # need to replot here for the size Hints to be computed correctly (depending on axis scales...)
        self.update()

    def setdata(self, fl, fh, fc, y):
        self.histogram.setData(fl, fh, fc, y)

        self.compute_peaks(y)
        self.bar_peak.setData(fl, fh, self.peak, self.peak_int, y)

        # only draw on demand
        # self.draw()

    def draw(self):
        if self.needfullreplot:
            self.needfullreplot = False

            self.verticalScaleTransform.setLength(self.canvasWidget.height())

            start_border, end_border = self.verticalScale.spacingBorders()
            self.verticalScaleTransform.setBorders(start_border, end_border)

            self.verticalScale.update()

            self.horizontalScaleTransform.setLength(self.canvasWidget.width())

            start_border, end_border = self.horizontalScale.spacingBorders()
            self.horizontalScaleTransform.setBorders(start_border, end_border)

            self.horizontalScale.update()

            x_major_tick = self.horizontalScaleDivision.majorTicks()
            x_minor_tick = self.horizontalScaleDivision.minorTicks()
            y_major_tick = self.verticalScaleDivision.majorTicks()
            y_minor_tick = self.verticalScaleDivision.minorTicks()
            self.canvasWidget.setGrid(array(x_major_tick),
                                      array(x_minor_tick),
                                      array(y_major_tick),
                                      array(y_minor_tick))

        self.canvasWidget.update()

    # redraw when the widget is resized to update coordinates transformations
    def resizeEvent(self, event):
        self.needfullreplot = True
        self.draw()

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
        self.verticalScaleTransform.setRange(spec_min, spec_max)
        self.verticalScaleDivision.setRange(spec_min, spec_max)

        # notify that sizeHint has changed (this should be done with a signal emitted from the scale division to the scale bar)
        self.verticalScale.scaleBar.updateGeometry()

        self.needfullreplot = True
        self.update()

    def setweighting(self, weighting):
        if weighting == 0:
            title = "PSD (dB)"
        elif weighting == 1:
            title = "PSD (dB A)"
        elif weighting == 2:
            title = "PSD (dB B)"
        else:
            title = "PSD (dB C)"

        self.verticalScale.setTitle(title)
