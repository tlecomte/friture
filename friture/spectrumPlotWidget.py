#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from friture.audiobackend import SAMPLING_RATE
from friture.plotting.scaleWidget import VerticalScaleWidget, HorizontalScaleWidget
from friture.plotting.scaleDivision import ScaleDivision
from friture.plotting.coordinateTransform import CoordinateTransform
from friture.plotting.glCanvasWidget import GlCanvasWidget
from friture.plotting.quadsItem import QuadsItem

from numpy import zeros, ones, log10, array
import numpy as np

# The peak decay rates (magic goes here :).
PEAK_DECAY_RATE = 1.0 - 3E-6
# Number of cycles the peak stays on hold before fall-off.
PEAK_FALLOFF_COUNT = 32  # default : 16

class SpectrumPlotWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(SpectrumPlotWidget, self).__init__(parent)

        self.x1 = array([0.1, 0.5, 1.])
        self.x2 = array([0.5, 1., 2.])

        self.needtransform = False

        self.paused = False

        self.peaks_enabled = True
        self.peak = zeros((3,))
        self.peak_int = zeros((3,))
        self.peak_decay = ones((3,)) * PEAK_DECAY_RATE

        self.verticalScaleDivision = ScaleDivision(0, 1, 100)
        self.verticalScaleTransform = CoordinateTransform(0, 1, 100, 0, 0)

        self.verticalScale = VerticalScaleWidget(self, self.verticalScaleDivision, self.verticalScaleTransform)
        self.verticalScale.setTitle("PSD (dB)")

        self.horizontalScaleDivision = ScaleDivision(0, 22000, 100)
        self.horizontalScaleTransform = CoordinateTransform(0, 22000, 100, 0, 0)

        self.horizontalScale = HorizontalScaleWidget(self, self.horizontalScaleDivision, self.horizontalScaleTransform)
        self.horizontalScale.setTitle("Frequency (Hz)")

        self.canvasWidget = GlCanvasWidget(self, self.verticalScaleTransform, self.horizontalScaleTransform)
        self.canvasWidget.setTrackerFormatter(lambda x, y: "%d Hz, %.1f dB" % (x, y))
        self.canvasWidget.resized.connect(self.canvasResized)

        r_peak = lambda p: 1. + 0.*p
        g_peak = lambda p: 1. - p
        b_peak = lambda p: 1. - p

        self.peakQuadsItem = QuadsItem(r_peak, g_peak, b_peak)
        self.canvasWidget.attach(self.peakQuadsItem)

        r_signal = lambda p: 0.*p
        g_signal = lambda p: 0.3 + 0.5*p
        b_signal = lambda p: 0.*p

        self.quadsItem = QuadsItem(r_signal, g_signal, b_signal)
        self.canvasWidget.attach(self.quadsItem)

        plotLayout = QtWidgets.QGridLayout()
        plotLayout.setSpacing(0)
        plotLayout.setContentsMargins(0, 0, 0, 0)
        plotLayout.addWidget(self.verticalScale, 0, 0)
        plotLayout.addWidget(self.canvasWidget, 0, 1)
        plotLayout.addWidget(self.horizontalScale, 1, 1)

        self.setLayout(plotLayout)

    def setlinfreqscale(self):
        self.horizontalScaleTransform.setLinear()
        self.horizontalScaleDivision.setLinear()

        self.needtransform = True
        self.draw()

    def setlogfreqscale(self):
        self.horizontalScaleTransform.setLogarithmic()
        self.horizontalScaleDivision.setLogarithmic()

        self.needtransform = True
        self.draw()

    def setfreqrange(self, minfreq, maxfreq):
        self.xmin = minfreq
        self.xmax = maxfreq

        self.horizontalScaleTransform.setRange(minfreq, maxfreq)
        self.horizontalScaleDivision.setRange(minfreq, maxfreq)

        # notify that sizeHint has changed (this should be done with a signal emitted from the scale division to the scale bar)
        self.horizontalScale.scaleBar.updateGeometry()

        self.needtransform = True
        self.draw()

    def setspecrange(self, spec_min, spec_max):
        if spec_min > spec_max:
            spec_min, spec_max = spec_max, spec_min

        self.verticalScaleTransform.setRange(spec_min, spec_max)
        self.verticalScaleDivision.setRange(spec_min, spec_max)

        # notify that sizeHint has changed (this should be done with a signal emitted from the scale division to the scale bar)
        self.verticalScale.scaleBar.updateGeometry()

        self.needtransform = True
        self.draw()

    def setweighting(self, weighting):
        if weighting is 0:
            title = "PSD (dB)"
        elif weighting is 1:
            title = "PSD (dB A)"
        elif weighting is 2:
            title = "PSD (dB B)"
        else:
            title = "PSD (dB C)"

        self.verticalScale.setTitle(title)
        self.needtransform = True
        self.draw()

    def setShowFreqLabel(self, showFreqLabel):
        self.canvasWidget.setShowFreqLabel(showFreqLabel)

    def set_peaks_enabled(self, enabled):
        self.peaks_enabled = enabled

        self.canvasWidget.detachAll()
        if enabled:
            self.canvasWidget.attach(self.peakQuadsItem)
        self.canvasWidget.attach(self.quadsItem)

    def set_baseline_displayUnits(self, baseline):
        self.quadsItem.set_baseline_displayUnits(baseline)

    def set_baseline_dataUnits(self, baseline):
        self.quadsItem.set_baseline_dataUnits(baseline)

    def setdata(self, x, y, fmax):
        x1 = zeros(x.shape)
        x2 = zeros(x.shape)
        x1[0] = 1e-10
        x1[1:] = (x[1:] + x[:-1]) / 2.
        x2[:-1] = x1[1:]
        x2[-1] = float(SAMPLING_RATE / 2)

        if len(x1) != len(self.x1):
            self.needtransform = True
            self.x1 = x1
            self.x2 = x2

        if not self.paused:
            self.canvasWidget.setfmax(fmax)

            M = max(y)
            m = self.verticalScaleTransform.coord_min
            y_int = (y-m)/(np.abs(M-m)+1e-3)

            self.quadsItem.setData(x1, x2, y, y_int)

            if self.peaks_enabled:
                self.compute_peaks(y)
                self.peakQuadsItem.setData(x1, x2, self.peak, self.peak_int)

    def draw(self):
        if self.needtransform:
            self.verticalScaleDivision.setLength(self.canvasWidget.height())
            self.verticalScaleTransform.setLength(self.canvasWidget.height())
            startBorder, endBorder = self.verticalScale.spacingBorders()
            self.verticalScaleTransform.setBorders(startBorder, endBorder)

            self.verticalScale.update()

            self.horizontalScaleDivision.setLength(self.canvasWidget.width())
            self.horizontalScaleTransform.setLength(self.canvasWidget.width())
            startBorder, endBorder = self.horizontalScale.spacingBorders()
            self.horizontalScaleTransform.setBorders(startBorder, endBorder)

            self.horizontalScale.update()

            self.canvasWidget.setGrid(array(self.horizontalScaleDivision.majorTicks()),
                                      array(self.horizontalScaleDivision.minorTicks()),
                                      array(self.verticalScaleDivision.majorTicks()),
                                      array(self.verticalScaleDivision.minorTicks()))

            self.quadsItem.transformUpdate()
            self.peakQuadsItem.transformUpdate()

            self.needtransform = False

    def pause(self):
        self.paused = True
        self.canvasWidget.pause()

    def restart(self):
        self.paused = False
        self.canvasWidget.restart()

    # redraw when the widget is resized to update coordinates transformations
    # QOpenGlWidget does not like that we override resizeEvent
    def canvasResized(self, canvasWidth, canvasHeight):
        self.needtransform = True
        self.draw()

    def canvasUpdate(self):
        self.canvasWidget.update()

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
