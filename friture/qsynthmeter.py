#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2004-2007, rncbc aka Rui Nuno Capela.
# Copyright (C) 2009 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http:#www.gnu.org/licenses/>.

from PyQt5 import QtCore, QtGui, QtWidgets

# Meter level limits (in dB).
MAXDB = +3.
MINDB = -70.

PEAK_DECAY_RATE = 1.0 - 3E-6

# Number of cycles the peak stays on hold before fall-off.
PEAK_FALLOFF = 32  # default : 16


# MeterScale -- Meter bridge scale widget.

class MeterScale(QtWidgets.QWidget):
    SEGMENTS_LEFT = 0
    SEGMENTS_BOTH = 1

    def __init__(self, meter, segmentsConf=SEGMENTS_LEFT):
        super().__init__(meter)
        self.meter = meter
        self.lastY = 0

        self.segmentsConf = segmentsConf

        self.setMinimumWidth(16)
        # self.setBackgroundRole(QPalette.Mid)

        self.setFont(QtGui.QFont(self.font().family(), 6))

    # Draw IEC scale line and label
    # assumes labels drawed from top to bottom
    def drawLineLabel(self, painter, y, label):
        currentY = self.height() - y
        scaleWidth = self.width()

        fontmetrics = painter.fontMetrics()
        labelMidHeight = fontmetrics.height() / 2

        # only draw the dB label if we are not too close to the top,
        # or too close to the previous label
        if currentY < labelMidHeight or currentY > self.lastY + labelMidHeight:
            # if the text label is small enough, draw horizontal segments on the side
            if fontmetrics.width(label) < scaleWidth - 5:
                self.drawSegments(painter, currentY, scaleWidth)

            # draw the text label (## dB)
            painter.drawText(0, currentY - labelMidHeight, scaleWidth - 1, fontmetrics.height(),
                             QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, label)

            self.lastY = currentY + 1

    # draw the horizontal segments next to the label
    def drawSegments(self, painter, y, scaleWidth):
        if self.segmentsConf in [self.SEGMENTS_LEFT, self.SEGMENTS_BOTH]:
            painter.drawLine(0, y, 2, y)

        if self.segmentsConf == self.SEGMENTS_BOTH:
            # if there are several meters, the scale is in-between
            # so the segments need to be drawn on both sides
            if self.meter.getPortCount() > 1:
                painter.drawLine(scaleWidth - 3, y, scaleWidth - 1, y)

    def setSegments(self, conf):
        self.segmentsConf = conf

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        self.lastY = 0

        painter.setPen(self.palette().mid().color().darker(200))

        for dB in [0, -3, -6, -10, -20, -30, -40, -50, -60]:
            self.drawLineLabel(painter, self.meter.iec_scale(dB), str(abs(dB)))


# BallisticPeak -- Peak with a value and a color, that holds then decays

class BallisticPeak:

    def __init__(self, meter):
        self.meter = meter  # used to reach IEC colors and levels
        self.peakValue = 0  # in pixels
        self.peakHoldCounter = 0
        self.peakDecayFactor = PEAK_DECAY_RATE
        self.peakColor = self.meter.Color6dB

    def value(self):
        return self.peakValue

    def color(self):
        return self.peakColor

    def reset(self):
        self.peakValue = 0

    def refresh(self, value):
        # peak-hold-then-decay mechanism
        peakValue = self.peakValue
        if peakValue < value:
            # the value is higher than the peak, the peak must follow the value
            peakValue = value
            self.peakHoldCounter = 0  # reset the hold
            self.peakDecayFactor = PEAK_DECAY_RATE
            self.peakColor = self.meter.Color10dB  # iLevel
            while self.peakColor > self.meter.ColorOver and peakValue >= self.meter.iec_level(self.peakColor):
                self.peakColor -= 1
        elif self.peakHoldCounter + 1 > self.meter.peakFalloff():
            peakValue = self.peakDecayFactor * float(peakValue)
            if self.peakValue < value:
                peakValue = value
            else:
                # if peakValue < self.meter.iec_level(self.meter.Color10dB):
                #    self.peakColor = self.meter.Color6dB
                self.peakDecayFactor *= self.peakDecayFactor
        self.peakHoldCounter += 1

        self.peakValue = peakValue

        return peakValue

# MeterValue -- Meter bridge value widget.


class MeterValue(QtWidgets.QFrame):

    def __init__(self, meter):
        super().__init__(meter)

        self.meter = meter
        self.dBValue = 0.0
        self.pixelValue = 0
        self.peak = BallisticPeak(self.meter)

        # a second indicator used when displaying both RMS and peak info
        # on the same meter
        self.dBValue2 = None
        self.pixelValue2 = 0

        self.paint_time = 0.

        self.setMinimumWidth(12)
        self.setBackgroundRole(QtGui.QPalette.NoRole)

    # Reset peak holder.
    def peakReset(self):
        self.peak.reset()

    def setValue(self, value, secondaryValue=None):
        self.dBValue = value
        self.dBValue = max(self.dBValue, MINDB)
        self.dBValue = min(self.dBValue, MAXDB)

        self.dBValue2 = secondaryValue
        if self.dBValue2 is not None:
            self.dBValue2 = max(self.dBValue2, MINDB)
            self.dBValue2 = min(self.dBValue2, MAXDB)

        self.refresh()

    def refresh(self):
        self.pixelValue = self.meter.iec_scale(self.dBValue)
        if self.dBValue2 is not None:
            self.pixelValue2 = self.meter.iec_scale(self.dBValue2)
            self.peak.refresh(max(self.pixelValue, self.pixelValue2))
        else:
            self.peak.refresh(self.pixelValue)
        self.update()

    def paintEvent(self, event):
        t = QtCore.QTime()
        t.start()

        painter = QtGui.QPainter(self)

        w = self.width()
        h = self.height()

        if self.isEnabled():
            painter.fillRect(0, 0, w, h,
                             self.meter.color(self.meter.ColorBack))
            y = self.meter.iec_level(self.meter.Color0dB)
            painter.setPen(self.meter.color(self.meter.ColorFore))
            painter.drawLine(0, h - y, w, h - y)
        else:
            painter.fillRect(0, 0, w, h, self.palette().darker().color())

        if self.pixelValue2 is not None:
            painter.drawPixmap(0, h - self.pixelValue2,
                               self.meter.darkPixmap(), 0, h - self.pixelValue2, w, self.pixelValue2 + 1)

        painter.drawPixmap(0, h - self.pixelValue,
                           self.meter.pixmap(), 0, h - self.pixelValue, w, self.pixelValue + 1)

        # draw the peak line
        painter.setPen(self.meter.color(self.peak.color()))
        painter.drawLine(0, h - self.peak.value(), w, h - self.peak.value())

        self.paint_time = (95. * self.paint_time + 5. * t.elapsed()) / 100.

    def resizeEvent(self, resizeEvent):
        self.peak.reset()

        QtWidgets.QWidget.resizeEvent(self, resizeEvent)
        # QtWidgets.QWidget.repaint(True)


# qsynthMeter -- Meter bridge slot widget.

class qsynthMeter(QtWidgets.QFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.portCount = 1

        self.IECScale = IECScale()

        self.levelPixmap = QtGui.QPixmap()
        self.darkLevelPixmap = QtGui.QPixmap()

        # Peak falloff mode setting (0=no peak falloff).
        self.peakFalloffCycleCount = PEAK_FALLOFF

        self.ColorOver = 0
        self.Color0dB = 1
        self.Color3dB = 2
        self.Color6dB = 3
        self.Color10dB = 4
        self.LevelCount = 5
        self.ColorBack = 5
        self.ColorFore = 6
        self.ColorCount = 7

        self.iecLevels = [0] * self.LevelCount

        self.colors = [QtGui.QColor(0, 0, 0)] * self.ColorCount
        self.colors[self.ColorOver] = QtGui.QColor(240, 0, 20)
        self.colors[self.Color0dB] = QtGui.QColor(240, 160, 20)
        self.colors[self.Color3dB] = QtGui.QColor(220, 220, 20)
        self.colors[self.Color6dB] = QtGui.QColor(160, 220, 20)
        self.colors[self.Color10dB] = QtGui.QColor(40, 160, 40)
        self.colors[self.ColorBack] = QtGui.QColor(20, 40, 20)
        self.colors[self.ColorFore] = QtGui.QColor(80, 80, 80)

        self.setBackgroundRole(QtGui.QPalette.NoRole)

        self.HBoxLayout = QtWidgets.QHBoxLayout()
        self.HBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.HBoxLayout.setSpacing(0)
        self.setLayout(self.HBoxLayout)

        self.build()

        self.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

    # build the widget layout depending on the port count.
    def build(self):
        # delete all elements of the current layout
        while self.HBoxLayout.count() > 0:
            item = self.HBoxLayout.takeAt(0)
            if not item:
                continue

            w = item.widget()
            if w:
                w.deleteLater()

        if self.portCount > 0:
            self.singleMeters = []
            self.singleScales = []

            if self.portCount == 1:
                self.singleMeters += [MeterValue(self)]
                self.HBoxLayout.addWidget(self.singleMeters[0])
                self.singleScales += [MeterScale(self, MeterScale.SEGMENTS_LEFT)]
                self.HBoxLayout.addWidget(self.singleScales[0])
            elif self.portCount < 4:
                for portIndex in range(0, self.portCount):
                    self.singleMeters += [MeterValue(self)]
                    self.HBoxLayout.addWidget(self.singleMeters[portIndex])
                    if portIndex < self.portCount - 1:
                        self.singleScales += [MeterScale(self, MeterScale.SEGMENTS_BOTH)]
                        self.HBoxLayout.addWidget(self.singleScales[portIndex])
            else:
                for portIndex in range(0, self.portCount):
                    self.singleMeters += [MeterValue(self)]
                    self.HBoxLayout.addWidget(self.singleMeters[portIndex])

                    # insert one scale only
                    if portIndex == 1:
                        self.singleScales += [MeterScale(self, MeterScale.SEGMENTS_BOTH)]
                        self.HBoxLayout.addWidget(self.singleScales[-1])
                    else:
                        # insert a spacer
                        self.HBoxLayout.addSpacing(1)

            self.setMinimumSize(16 * self.portCount + 16 * len(self.singleScales), 120)
            self.setMaximumWidth(16 * self.portCount + 16 * len(self.singleScales))
        else:  # zero meters
            self.setMinimumSize(2, 120)
            self.setMaximumWidth(4)

    # used by child widgets
    def iec_scale(self, dB):
        return self.IECScale.iec_scale(dB)

    def iec_level(self, index):
        return self.iecLevels[index]

    def getPortCount(self):
        return self.portCount

    def setPortCount(self, count):
        self.portCount = count
        self.build()

    def setPeakFalloff(self, peakFalloffCount):
        self.peakFalloffCycleCount = peakFalloffCount

    def peakFalloff(self):
        return self.peakFalloffCycleCount

    # Reset peak holder.
    def peakReset(self):
        for port in range(0, self.portCount):
            self.singleMeters[port].peakReset()

    def pixmap(self):
        return self.levelPixmap

    def darkPixmap(self):
        return self.darkLevelPixmap

    def updatePixmap(self):
        w = self.width()
        h = self.height()

        grad = QtGui.QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.2, self.color(self.ColorOver))
        grad.setColorAt(0.3, self.color(self.Color0dB))
        grad.setColorAt(0.4, self.color(self.Color3dB))
        grad.setColorAt(0.6, self.color(self.Color6dB))
        grad.setColorAt(0.8, self.color(self.Color10dB))
        grad = QtGui.QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QtGui.QColor(230, 230, 255))
        grad.setColorAt(0.7, QtGui.QColor(0, 0, 255))
        grad.setColorAt(1.0, QtGui.QColor(0, 0, 150))

        self.levelPixmap = QtGui.QPixmap(w, h)
        QtGui.QPainter(self.levelPixmap).fillRect(0, 0, w, h, grad)

        factor = 0  # 150
        darkGrad = QtGui.QLinearGradient(0, 0, 0, h)
        darkGrad.setColorAt(0.2, self.color(self.ColorOver).darker(factor))
        darkGrad.setColorAt(0.3, self.color(self.Color0dB).darker(factor))
        darkGrad.setColorAt(0.4, self.color(self.Color3dB).darker(factor))
        darkGrad.setColorAt(0.6, self.color(self.Color6dB).darker(factor))
        darkGrad.setColorAt(0.8, self.color(self.Color10dB).darker(factor))

        self.darkLevelPixmap = QtGui.QPixmap(w, h)
        QtGui.QPainter(self.darkLevelPixmap).fillRect(0, 0, w, h, darkGrad)

    def refresh(self):
        for iPort in range(0, self.portCount):
            self.singleMeters[iPort].refresh()

    def resizeEvent(self, event):
        self.IECScale.setHeight(0.95 * float(self.height()))

        self.iecLevels[self.Color0dB] = self.iec_scale(0.0)
        self.iecLevels[self.Color3dB] = self.iec_scale(-3.0)
        self.iecLevels[self.Color6dB] = self.iec_scale(-6.0)
        self.iecLevels[self.Color10dB] = self.iec_scale(-10.0)

        self.updatePixmap()

    def setValue(self, port, value, secondaryValue=None):
        self.singleMeters[port].setValue(value, secondaryValue)

    def color(self, index):
        return self.colors[index]


# class to translate from dB to pixels with an IEC scaling
class IECScale:

    def __init__(self):
        self.height = 1.

    def setHeight(self, height):
        self.height = height

    def iec_scale(self, dB):
        fDef = 1.

        if dB < -70.0:
            fDef = 0.0
        elif dB < -60.0:
            fDef = (dB + 70.0) * 0.0025
        elif dB < -50.0:
            fDef = (dB + 60.0) * 0.005 + 0.025
        elif dB < -40.0:
            fDef = (dB + 50.0) * 0.0075 + 0.075
        elif dB < -30.0:
            fDef = (dB + 40.0) * 0.015 + 0.15
        elif dB < -20.0:
            fDef = (dB + 30.0) * 0.02 + 0.3
        else:  # if dB < 0.0
            fDef = (dB + 20.0) * 0.025 + 0.5

        return fDef * self.height
