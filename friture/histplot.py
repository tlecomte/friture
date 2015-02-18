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

from PyQt5 import QtCore, Qt, QtGui, QtWidgets
from numpy import zeros, ones, log10, linspace, logspace, log2, array, round
from friture.plotting.scaleWidget import VerticalScaleWidget, HorizontalScaleWidget
from friture.plotting.scaleDivision import ScaleDivision
from friture.plotting.coordinateTransform import CoordinateTransform
from friture.plotting.canvasWidget import CanvasWidget

# The peak decay rates (magic goes here :).
PEAK_DECAY_RATE = 1.0 - 3E-6
# Number of cycles the peak stays on hold before fall-off.
PEAK_FALLOFF_COUNT = 32 # default : 16

class HistogramItem:
    def __init__(self, *args):

        self.__color = Qt.QColor()

        self.cached_bar_width = 1
        self.canvas_height = 2
        self.canvas_width = 2
        self.need_transform = False
        self.fl = [0.]
        self.fh = [0.]
        self.fc = ["0"] # center frequencies
        self.y = array([0.])
        self.i = [0]

        self.pixmaps = [QtGui.QPixmap()]
        self.maxLabelPixHWidth = 0
        self.maxLabelPixVWidth = 0
        self.pixHWidths = 0
        self.pixVWidths = 0
        self.pixHHeights = 0
        self.pixVHeights = 0
        self.Hpixmaps = [[QtGui.QPixmap(), QtGui.QPixmap()]]
        self.Vpixmaps = [[QtGui.QPixmap(), QtGui.QPixmap()]]

    def setData(self, fl, fh, fc, y):
        if len(self.y) != len(y):
            self.fl = fl
            self.fh = fh
            self.fc = fc
            self.need_transform = True
            self.update_labels_pixmap(self.fc)

        self.y = array(y)

    def data(self):
        return self.__data

    def setColor(self, color):
        if self.__color != color:
            self.__color = color

    def color(self):
        return self.__color

    def draw(self, painter, xMap, yMap, rect):
        # update the cache according to possibly new canvas dimensions
        h = rect.height()
        if h != self.canvas_height:
            self.canvas_height = h
            self.need_transform = True
        w = rect.width()
        if w < self.canvas_width - 1 or w > self.canvas_width + 1:
            self.canvas_width = w
            self.need_transform = True

        # update the cached pixmaps and coordinates if necessary
        if self.need_transform:
            # round to pixels
            self.x1 = round(xMap.toScreen(array(self.fl)))
            self.x2 = round(xMap.toScreen(array(self.fh)))-1

            self.update_pixmap(self.x2[0] - self.x1[0], self.canvas_height)
            self.i = list(array(self.x2) - array(self.x1) - (self.cached_bar_width - 2))

            self.need_transform = False

        y = self.canvas_height - yMap.toScreen(self.y)

        for x1, x2, y2, i in zip(self.x1, self.x2, y, self.i):
            self.drawBar(painter, x1, y2, i)

        w = self.x2[0] - self.x1[0]

        if self.maxLabelPixHWidth <= w: # try to draw the frequency labels horizontally
            self.drawLabels(painter, y, self.pixHWidths, self.pixHHeights, self.Hpixmaps)
        elif self.maxLabelPixVWidth <= w: # try to draw the frequency labels vertically
            self.drawLabels(painter, y, self.pixVWidths, self.pixVHeights, self.Vpixmaps)

    def drawLabels(self, painter, y, pixWidths, pixHeights, pixmaps):
        x = (self.x1 + self.x2)/2 - pixWidths/2 # center

        Dy = 6
        y += Dy # some margin between top of the bar and text

        hBound = 3
        y = (y>=hBound)*y + (y<hBound)*hBound

        mask = y + pixHeights >= self.canvas_height-1
        y = mask*(self.canvas_height-hBound-pixHeights) + (-mask)*y
        ps = mask*1 + (-mask)*0

        for x1, y2, p, pixmap in zip(x, y, ps, pixmaps):
            painter.drawPixmap(x1, y2, pixmap[p])

    def drawBar(self, painter, left, top, i):
        painter.drawPixmap(int(left), int(top), self.pixmaps[int(i)])

    # For a dramatic speedup, the bars are cached instead of drawn from scratch each time
    def update_pixmap(self, width, height):
        self.cached_bar_width = width

        color = QtGui.QColor(self.color())

        self.pixmaps = []
        for w in range(int(width)-2, int(width)+3):
            pixmap = QtGui.QPixmap(w+1, height+1)
            pixmap.fill(color)
            painter = QtGui.QPainter(pixmap)
            if width > 3:
                self.drawBarDecoration(painter, w, height)
            self.pixmaps += [pixmap]

    def drawBarDecoration(self, painter, width, height):
        color = QtGui.QColor(self.color())
        factor = 125
        light = color.lighter(factor)
        dark = color.darker(factor)

        painter.setBrush(Qt.Qt.NoBrush)

        top = 0
        bottom = height
        left = 0
        right = width - 1

        #horizontal line
        painter.setPen(Qt.QPen(light, 2))
        painter.drawLine(1, top+2, right+1, top+2)

        #horizontal line
        painter.setPen(Qt.QPen(dark, 2))
        painter.drawLine(1, bottom, right+1, bottom)

        #vertical line
        painter.setPen(Qt.QPen(light, 1))
        painter.drawLine(0, top + 1, 0, bottom)
        painter.drawLine(1, top + 2, 1, bottom-1)

        #vertical line
        painter.setPen(Qt.QPen(dark, 1))
        painter.drawLine(right+1, top+1, right+1, bottom)
        painter.drawLine(right, top+2, right, bottom-1)

    # For a dramatic speedup, the frequency labels are cached
    # instead of drawn from scratch each time
    def update_labels_pixmap(self, fList):
        labels_pixmaps_H_black = []
        labels_pixmaps_H_white = []
        labels_pixmaps_V_black = []
        labels_pixmaps_V_white = []

        w = h = 1
        test_pixmap = QtGui.QPixmap(w, h)
        test_pixmap.fill()
        test_painter = QtGui.QPainter(test_pixmap)
        fRect = QtCore.QRectF(0, 0, w, h)

        transparentColor = QtGui.QColor(0,0,0,0)

        for f in fList:
            # first, find the right pixmap size
            bRect = test_painter.boundingRect(fRect, Qt.Qt.AlignLeft, f)

            # second, create the pixmap with the right size
            pixmap = QtGui.QPixmap(bRect.width(), bRect.height())
            pixmap.fill(transparentColor) # transparent background
            painter = QtGui.QPainter(pixmap)
            painter.setPen(QtCore.Qt.black)
            painter.drawText(bRect, Qt.Qt.AlignLeft, f)
            labels_pixmaps_H_black += [pixmap]

            pixmap = QtGui.QPixmap(bRect.width(), bRect.height())
            pixmap.fill(transparentColor) # transparent background
            painter = QtGui.QPainter(pixmap)
            painter.setPen(QtCore.Qt.white)
            painter.drawText(bRect, Qt.Qt.AlignLeft, f)
            labels_pixmaps_H_white += [pixmap]

        angle = -90
        for pix in labels_pixmaps_H_black:
            pixmap = QtGui.QPixmap(pix.height(), pix.width())
            pixmap.fill(transparentColor) # transparent background
            painter = QtGui.QPainter(pixmap)
            painter.rotate(angle)
            painter.drawPixmap(-pix.width(), 0, pix)
            labels_pixmaps_V_black += [pixmap]

        for pix in labels_pixmaps_H_white:
            pixmap = QtGui.QPixmap(pix.height(), pix.width())
            pixmap.fill(transparentColor) # transparent background
            painter = QtGui.QPainter(pixmap)
            painter.rotate(angle)
            painter.drawPixmap(-pix.width(), 0, pix)
            labels_pixmaps_V_white += [pixmap]

        test_painter.end() # manually ends painting to satisfy Qt

        self.pixHWidths = array([pix.width() for pix in labels_pixmaps_H_white])
        self.maxLabelPixHWidth = max(self.pixHWidths)
        self.pixHHeights = array([pix.height() for pix in labels_pixmaps_H_white])

        self.pixVWidths = array([pix.width() for pix in labels_pixmaps_V_white])
        self.maxLabelPixVWidth = max(self.pixVWidths)
        self.pixVHeights = array([pix.height() for pix in labels_pixmaps_V_white])

        self.Hpixmaps = [[pix_white, pix_black] for pix_white, pix_black in zip(labels_pixmaps_H_white,
                                                                                labels_pixmaps_H_black)]

        self.Vpixmaps = [[pix_white, pix_black] for pix_white, pix_black in zip(labels_pixmaps_V_white,
                                                                                labels_pixmaps_V_black)]


class HistogramPeakBarItem:
    def __init__(self, *args):
        self.fl = [0.]
        self.fh = [0.]
        self.peaks = array([0.])
        self.palette_index = [0]
        self.y = array([0.])
        self.canvas_width = 2
        self.need_transform = False
        self.yMap = None

        self.palette = [Qt.QColor(255, gb, gb) for gb in range(0,256)]

    def setData(self, fl, fh, peaks, peaks_int, y):
        if len(self.peaks) != len(peaks):
            self.fl = fl
            self.fh = fh
            self.need_transform = True

        self.peaks = peaks
        self.palette_index = (255*(1.-peaks_int)).astype(int)
        self.y = array(y)

    def draw(self, painter, xMap, yMap, rect):
        # update the cache according to possibly new canvas dimensions
        h = rect.height()
        w = rect.width()
        if w != self.canvas_width:
            self.canvas_width = w
            self.need_transform = True

        if self.need_transform:
            # round to pixels
            self.x1 = round(xMap.toScreen(array(self.fl)))
            self.x2 = round(xMap.toScreen(array(self.fh)))

            self.need_transform = False

        peaks = h - yMap.toScreen(self.peaks)
        ys  = h - yMap.toScreen(self.y)

        for x1, x2, peak, index, y in zip(self.x1, self.x2, peaks, self.palette_index, ys):
            painter.fillRect(x1, peak, x2-x1, y-peak+1, self.palette[index])


class HistPlot(QtWidgets.QWidget):
    def __init__(self, parent, logger):
        super(HistPlot, self).__init__()

        # store the logger instance
        self.logger = logger

        self.verticalScaleDivision = ScaleDivision(-140, 0, 100)
        self.verticalScaleTransform = CoordinateTransform(-140, 0, 100, 0, 0)

        self.verticalScale = VerticalScaleWidget(self, self.verticalScaleDivision, self.verticalScaleTransform)
        self.verticalScale.setTitle("PSD (dB A)")

        self.horizontalScaleDivision = ScaleDivision(44, 22000, 100)
        self.horizontalScaleTransform = CoordinateTransform(44, 22000, 100, 0, 0)

        self.horizontalScale = HorizontalScaleWidget(self, self.horizontalScaleDivision, self.horizontalScaleTransform)
        self.horizontalScale.setTitle("Frequency (Hz)")

        self.canvasWidget = CanvasWidget(self, self.verticalScaleTransform, self.horizontalScaleTransform)
        self.canvasWidget.setTrackerFormatter(lambda x, y: "%d Hz, %.1f dB" %(x, y))

        plotLayout = QtWidgets.QGridLayout()
        plotLayout.setSpacing(0)
        plotLayout.setContentsMargins(0, 0, 0, 0)
        plotLayout.addWidget(self.verticalScale, 0, 0)
        plotLayout.addWidget(self.canvasWidget, 0, 1)
        plotLayout.addWidget(self.horizontalScale, 1, 1)

        self.setLayout(plotLayout)

        self.needfullreplot = False

        self.horizontalScaleTransform.setLogarithmic()
        self.horizontalScaleDivision.setLogarithmic()

        # insert an additional plot item for the peak bar
        self.bar_peak = HistogramPeakBarItem()
        self.canvasWidget.attach(self.bar_peak)
        self.peak = zeros((1,))
        self.peak_int = 0
        self.peak_decay = PEAK_DECAY_RATE

        self.histogram = HistogramItem()
        self.histogram.setColor(Qt.Qt.darkGreen)
        self.canvasWidget.attach(self.histogram)

        #need to replot here for the size Hints to be computed correctly (depending on axis scales...)
        self.update()

    def setdata(self, fl, fh, fc, y):
        self.histogram.setData(fl, fh, fc, y)

        self.compute_peaks(y)
        self.bar_peak.setData(fl, fh, self.peak, self.peak_int, y)

        self.draw()

    def draw(self):
        if self.needfullreplot:
            self.needfullreplot = False

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

            xMajorTick = self.horizontalScaleDivision.majorTicks()
            xMinorTick = self.horizontalScaleDivision.minorTicks()
            yMajorTick = self.verticalScaleDivision.majorTicks()
            yMinorTick = self.verticalScaleDivision.minorTicks()
            self.canvasWidget.setGrid(array(xMajorTick),
                                      array(xMinorTick),
                                      array(yMajorTick),
                                      array(yMinorTick)
                                      )

        self.canvasWidget.update()

    # redraw when the widget is resized to update coordinates transformations
    def resizeEvent(self, event):
        self.needfullreplot = True
        self.draw()

    def compute_peaks(self, y):
        if len(self.peak) != len(y):
            y_ones = ones(y.shape)
            self.peak = y_ones*(-500.)
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

    def setspecrange(self, min, max):
        self.verticalScaleTransform.setRange(min, max)
        self.verticalScaleDivision.setRange(min, max)

        # notify that sizeHint has changed (this should be done with a signal emitted from the scale division to the scale bar)
        self.verticalScale.scaleBar.updateGeometry()

        self.needfullreplot = True
        self.update()

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
