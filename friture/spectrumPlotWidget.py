#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtWidgets
from friture.audiobackend import SAMPLING_RATE
from friture.plotting.scaleWidget import VerticalScaleWidget, HorizontalScaleWidget
from friture.plotting.scaleDivision import ScaleDivision
from friture.plotting.coordinateTransform import CoordinateTransform
from friture.plotting.glCanvasWidget import GlCanvasWidget

try:
    from OpenGL import GL
except ImportError:
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None, "OpenGL hellogl",
                                   "PyOpenGL must be installed to run this example.")
    sys.exit(1)

from numpy import zeros, ones, log10, hstack, array, floor, mean, where
import numpy as np

# The peak decay rates (magic goes here :).
PEAK_DECAY_RATE = 1.0 - 3E-6
# Number of cycles the peak stays on hold before fall-off.
PEAK_FALLOFF_COUNT = 32  # default : 16


def pre_tree_rebin(x1, x2):
    if len(x2) == 0:
        # enf of recursion !
        return x1, x2, 0

    bins = where(x2 - x1 >= 0.5)[0]

    if len(bins) == 0:
        n0 = len(x2)
    else:
        n0 = max(where(x2 - x1 >= 0.5)[0])

    # leave untouched the frequency bins that span more than half a pixel
    # and first make sure that what will be left can be decimated by two
    rest = len(x2) - n0 - ((len(x2) - n0) // 2) * 2

    n0 += rest

    x1_0 = x1[:n0]
    x2_0 = x2[:n0]

    # decimate the rest
    x1_2 = x1[n0::2]
    x2_2 = x2[n0 + 1::2]

    # recursive !!
    x1_2, x2_2, n2 = pre_tree_rebin(x1_2, x2_2)

    if n2 == 0.:
        n = [n0]
    else:
        n = [n0] + [i * 2 + n0 for i in n2]

    x1 = hstack((x1_0, x1_2))
    x2 = hstack((x2_0, x2_2))

    return x1, x2, n


def tree_rebin(y, ns, N):
    y2 = zeros(N)

    n = 0
    for i in range(len(ns) - 1):
        y3 = y[ns[i]:ns[i + 1]]
        d = 2 ** i
        l = len(y3) / d
        y3.shape = (l, d)

        # Note: the FFT spectrum is mostly used to identify frequency content
        # ans _peaks_ are particularly interesting (e.g. feedback frequencies)
        # so we display the _max_ instead of the mean of each bin
        # y3 = mean(y3, axis=1)
        # y3 = (y3[::2] + y3[1::2])*0.5

        y3 = np.max(y3, axis=1)

        y2[n:n + len(y3)] = y3
        n += l

    return y2


class SpectrumPlotWidget(QtWidgets.QWidget):

    def __init__(self, parent, logger=None):
        super(SpectrumPlotWidget, self).__init__(parent)

        self.x1 = array([0.1, 0.5, 1.])
        self.x2 = array([0.5, 1., 2.])

        self.needtransform = False

        self.paused = False

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

        self.quadsItem = QuadsItem()
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
        self.quadsItem.set_peaks_enabled(enabled)

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
            self.quadsItem.setData(x1, x2, y)

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


class QuadsItem:

    def __init__(self, *args):
        self.peaks_enabled = True
        self.peak = zeros((3,))
        self.peak_int = zeros((3,))
        self.peak_decay = ones((3,)) * PEAK_DECAY_RATE

        self.x1 = array([0.1, 0.5, 1.])
        self.x2 = array([0.5, 1., 2.])
        self.y = array([0., 0., 0.])

        self.transformed_x1 = self.x1
        self.transformed_x2 = self.x2

        self.need_transform = True

        self.baseline_transformed = False
        self.baseline = 0.

        self.vertices = array([])
        self.colors = array([])

    def set_peaks_enabled(self, enabled):
        self.peaks_enabled = enabled

    def set_baseline_displayUnits(self, baseline):
        self.baseline_transformed = False
        self.baseline = baseline

    def set_baseline_dataUnits(self, baseline):
        self.baseline_transformed = True
        self.baseline = baseline

    def setData(self, x1, x2, y):
        if len(x1) != len(self.x1):
            self.need_transform = True

        self.x1 = x1
        self.x2 = x2
        self.y = y

    def prepareQuadData(self, x, y, w, baseline, r, g, b):
        h = y - baseline
        y = baseline

        n = x.shape[0]

        self.vertices = zeros((n, 4, 2))
        self.vertices[:, 0, 0] = x
        self.vertices[:, 0, 1] = y + h
        self.vertices[:, 1, 0] = x + w
        self.vertices[:, 1, 1] = y + h
        self.vertices[:, 2, 0] = x + w
        self.vertices[:, 2, 1] = y
        self.vertices[:, 3, 0] = x
        self.vertices[:, 3, 1] = y

        self.colors = zeros((n, 4, 3))
        self.colors[:, 0, 0] = r
        self.colors[:, 1, 0] = r
        self.colors[:, 2, 0] = r
        self.colors[:, 3, 0] = r
        self.colors[:, 0, 1] = g
        self.colors[:, 1, 1] = g
        self.colors[:, 2, 1] = g
        self.colors[:, 3, 1] = g
        self.colors[:, 0, 2] = b
        self.colors[:, 1, 2] = b
        self.colors[:, 2, 2] = b
        self.colors[:, 3, 2] = b

    def transformUpdate(self):
        self.need_transform = True

    def glDraw(self, xMap, yMap, rect):
        # transform the coordinates only when needed
        if self.need_transform:
            self.transformed_x1 = xMap.toScreen(self.x1)
            self.transformed_x2 = xMap.toScreen(self.x2)

            if xMap.log:
                self.transformed_x1, self.transformed_x2, n = pre_tree_rebin(self.transformed_x1, self.transformed_x2)
                self.n = [0] + n
                self.N = 0
                for i in range(len(self.n) - 1):
                    self.N += (self.n[i + 1] - self.n[i]) / 2 ** i

            self.need_transform = False

        # for easier reading
        x1 = self.transformed_x1
        x2 = self.transformed_x2

        if xMap.log:
            y = tree_rebin(self.y, self.n, self.N)
        else:
            n = int(floor(1. / (x2[2] - x1[1])))
            if n > 1:
                new_len = len(self.y) // n
                rest = len(self.y) - new_len * n

                new_y = self.y[:-rest]
                new_y.shape = (new_len, n)
                y = mean(new_y, axis=1)

                x1 = x1[:-rest:n]
                x2 = x2[n::n]
            else:
                y = self.y

        if self.peaks_enabled:
            self.compute_peaks(y)

        transformed_y = yMap.toScreen(y)

        Ones = ones(x1.shape)

        if self.peaks_enabled:
            transformed_peak = yMap.toScreen(self.peak)

            n = x1.size

            # TODO: should be done conditionally to need_transform
            x1_with_peaks = zeros((2 * n))
            x2_with_peaks = zeros((2 * n))
            y_with_peaks = zeros((2 * n))
            r_with_peaks = zeros((2 * n))
            g_with_peaks = zeros((2 * n))
            b_with_peaks = zeros((2 * n))

            x1_with_peaks[:n] = x1
            x1_with_peaks[n:] = x1

            x2_with_peaks[:n] = x2
            x2_with_peaks[n:] = x2

            y_with_peaks[:n] = transformed_peak
            y_with_peaks[n:] = transformed_y

            r_with_peaks[:n] = 1. * Ones
            r_with_peaks[n:] = 0. * Ones

            g_with_peaks[:n] = 1. - self.peak_int
            g_with_peaks[n:] = 0.5 * Ones

            b_with_peaks[:n] = 1. - self.peak_int
            b_with_peaks[n:] = 0. * Ones
        else:
            x1_with_peaks = x1
            x2_with_peaks = x2
            y_with_peaks = transformed_y
            r_with_peaks = 0. * Ones
            g_with_peaks = 0.5 * Ones
            b_with_peaks = 0. * Ones

        if self.baseline_transformed:
            # used for dual channel response measurement
            baseline = yMap.toScreen(self.baseline)
        else:
            # used for single channel analysis
            baseline = self.baseline

        self.prepareQuadData(x1_with_peaks, y_with_peaks, x2_with_peaks - x1_with_peaks, baseline, r_with_peaks, g_with_peaks, b_with_peaks)

        # TODO: instead of Arrays, VBOs should be used here, as a large part of
        # the data does not have to be modified on every call (x coordinates,
        # green colored quads)

        # TODO: If the arrays could be drawn as SHORTs istead of FLOATs, it
        # could also be dramatically faster

        GL.glVertexPointerd(self.vertices)
        GL.glColorPointerd(self.colors)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)

        # GL.glDisable(GL.GL_LIGHTING)
        GL.glDrawArrays(GL.GL_QUADS, 0, 4 * self.vertices.shape[0])
        # GL.glEnable(GL.GL_LIGHTING)

        GL.glDisableClientState(GL.GL_COLOR_ARRAY)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

    def compute_peaks(self, y):
        if len(self.peak) != len(y):
            y_ones = ones(y.shape)
            self.peak = y_ones * (-500.)
            self.peak_int = zeros(y.shape)
            self.peak_decay = y_ones * 20. * log10(PEAK_DECAY_RATE) * 5000

        mask1 = (self.peak < y)
        mask2 = (-mask1)
        mask2_a = mask2 * (self.peak_int < 0.2)
        mask2_b = mask2 * (self.peak_int >= 0.2)

        self.peak[mask1] = y[mask1]
        self.peak[mask2_a] = self.peak[mask2_a] + self.peak_decay[mask2_a]

        self.peak_decay[mask1] = 20. * log10(PEAK_DECAY_RATE) * 5000
        self.peak_decay[mask2_a] += 20. * log10(PEAK_DECAY_RATE) * 5000

        self.peak_int[mask1] = 1.
        self.peak_int[mask2_b] *= 0.975
