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

from OpenGL.GL import shaders
from ctypes import sizeof, c_float, c_void_p, c_uint

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
        l = len(y3) // d
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


class QuadsItem:

    def __init__(self, r, g, b, *args):
        self.x1 = array([0.1, 0.5, 1.])
        self.x2 = array([0.5, 1., 2.])
        self.y = array([0., 0., 0.])
        self.y_int = array([0., 0., 0.])

        self.r = r
        self.g = g
        self.b = b

        self.transformed_x1 = self.x1
        self.transformed_x2 = self.x2

        self.need_transform = True

        self.baseline_transformed = False
        self.baseline = 0.

        self.vertices_data = array([], dtype=np.float32)

    def set_baseline_displayUnits(self, baseline):
        self.baseline_transformed = False
        self.baseline = baseline

    def set_baseline_dataUnits(self, baseline):
        self.baseline_transformed = True
        self.baseline = baseline

    def setData(self, x1, x2, y, y_int):
        if len(x1) != len(self.x1):
            self.need_transform = True

        self.x1 = x1
        self.x2 = x2
        self.y = y
        self.y_int = y_int

    def prepareQuadData(self, x, y, w, baseline, r, g, b):
        h = y - baseline
        y = baseline + 0.*y

        n = x.shape[0]

        # 4 vertices per quad * (3 coordinates + 3 color coordinates)
        if self.vertices_data.shape != (n*4, 6):
            self.vertices_data = zeros((n*4, 6), dtype=np.float32)

        self.vertices_data[0::4, 0::6] = x[:,np.newaxis]
        self.vertices_data[0::4, 1::6] = (y + h)[:,np.newaxis]
        self.vertices_data[0::4, 2::6] = 0*x[:,np.newaxis]
        self.vertices_data[0::4, 3::6] = r[:,np.newaxis]
        self.vertices_data[0::4, 4::6] = g[:,np.newaxis]
        self.vertices_data[0::4, 5::6] = b[:,np.newaxis]

        self.vertices_data[1::4, 0::6] = (x + w)[:,np.newaxis]
        self.vertices_data[1::4, 1::6] = (y + h)[:,np.newaxis]
        self.vertices_data[1::4, 2::6] = 0*x[:,np.newaxis]
        self.vertices_data[1::4, 3::6] = r[:,np.newaxis]
        self.vertices_data[1::4, 4::6] = g[:,np.newaxis]
        self.vertices_data[1::4, 5::6] = b[:,np.newaxis]

        self.vertices_data[2::4, 0::6] = x[:,np.newaxis]
        self.vertices_data[2::4, 1::6] = y[:,np.newaxis]
        self.vertices_data[2::4, 2::6] = 0*x[:,np.newaxis]
        self.vertices_data[2::4, 3::6] = r[:,np.newaxis]
        self.vertices_data[2::4, 4::6] = g[:,np.newaxis]
        self.vertices_data[2::4, 5::6] = b[:,np.newaxis]

        self.vertices_data[3::4, 0::6] = (x + w)[:,np.newaxis]
        self.vertices_data[3::4, 1::6] = y[:,np.newaxis]
        self.vertices_data[3::4, 2::6] = 0*x[:,np.newaxis]
        self.vertices_data[3::4, 3::6] = r[:,np.newaxis]
        self.vertices_data[3::4, 4::6] = g[:,np.newaxis]
        self.vertices_data[3::4, 5::6] = b[:,np.newaxis]

    def transformUpdate(self):
        self.need_transform = True

    def glDraw(self, xMap, yMap, rect, vbo, shader_program):
        # transform the coordinates only when needed
        if self.need_transform:
            self.transformed_x1 = xMap.toScreen(self.x1)
            self.transformed_x2 = xMap.toScreen(self.x2)

            if xMap.log:
                self.transformed_x1, self.transformed_x2, n = pre_tree_rebin(self.transformed_x1, self.transformed_x2)
                self.n = [0] + n
                self.N = 0
                for i in range(len(self.n) - 1):
                    self.N += (self.n[i + 1] - self.n[i]) // 2 ** i

            self.need_transform = False

        # for easier reading
        x1 = self.transformed_x1
        x2 = self.transformed_x2

        if xMap.log:
            y = tree_rebin(self.y, self.n, self.N)
            y_int = tree_rebin(self.y_int, self.n, self.N)
        else:
            n = int(floor(1. / (x2[2] - x1[1])))
            if n > 1:
                new_len = len(self.y) // n
                rest = len(self.y) - new_len * n

                new_y = self.y[:-rest]
                new_y.shape = (new_len, n)
                y = mean(new_y, axis=1)

                new_y_int = self.y_int[:-rest]
                new_y_int.shape = (new_len, n)
                y_int = mean(new_y_int, axis=1)

                x1 = x1[:-rest:n]
                x2 = x2[n::n]
            else:
                y = self.y
                y_int = self.y_int

        transformed_y = yMap.toScreen(y)

        r = self.r(y_int)
        g = self.g(y_int)
        b = self.b(y_int)

        if self.baseline_transformed:
            # used for dual channel response measurement
            baseline = yMap.toScreen(self.baseline)
        else:
            # used for single channel analysis
            baseline = self.baseline

        self.prepareQuadData(x1, transformed_y, x2 - x1, baseline, r, g, b)

        vbo.set_array(self.vertices_data)

        vbo.bind()
        try:
            GL.glEnableVertexAttribArray(0)
            GL.glEnableVertexAttribArray(1)
            stride = self.vertices_data.shape[-1]*sizeof(c_float)
            vertex_offset = c_void_p(0 * sizeof(c_float))
            color_offset  = c_void_p(3 * sizeof(c_float))
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, vertex_offset)
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, color_offset)
            GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, self.vertices_data.shape[0])
            GL.glDisableVertexAttribArray(0)
            GL.glDisableVertexAttribArray(1)
        finally:
            vbo.unbind()
