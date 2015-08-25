#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Timothée Lecomte

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

from PyQt5 import QtCore, QtGui, QtWidgets

from .grid import Grid


class CanvasWidget(QtWidgets.QWidget):

    resized = QtCore.pyqtSignal(int, int)

    def __init__(self, parent, verticalScaleTransform, horizontalScaleTransform):
        super(CanvasWidget, self).__init__(parent)

        # set proper size policy for this widget
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))

        self.setAutoFillBackground(False)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)

        self.horizontalScaleTransform = horizontalScaleTransform
        self.verticalScaleTransform = verticalScaleTransform

        self.lastPos = QtCore.QPoint()
        self.ruler = False
        self.mousex = 0
        self.mousey = 0

        # use a cross cursor to easily select a point on the graph
        self.setCursor(QtCore.Qt.CrossCursor)

        self.attachedItems = []

        self.grid = Grid()

        self.trackerFormatter = lambda x, y: "x=%d, y=%d" % (x, y)

        self.anyOpaqueItem = False

    def setTrackerFormatter(self, formatter):
        self.trackerFormatter = formatter

    def sizeHint(self):
        return QtCore.QSize(50, 50)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        self.drawBackground(painter)
        self.drawData(painter)
        self.drawRuler(painter)
        self.drawBorder(painter)

        self.drawTrackerText(painter)
        painter.end()

    def resizeEvent(self, event):
        # give the opportunity to the scales to adapt
        self.resized.emit(self.width(), self.height())

    def attach(self, item):
        self.attachedItems.append(item)
        self.reviewOpaqueItems()

    def detach(self, item):
        self.attachedItems.remove(item)
        self.reviewOpaqueItems()

    def reviewOpaqueItems(self):
        self.anyOpaqueItem = False
        for item in self.attachedItems:
            try:
                if item.isOpaque():
                    self.anyOpaqueItem = True
            except:
                # do nothing
                continue

    def drawData(self, painter):
        for item in self.attachedItems:
            item.draw(painter, self.horizontalScaleTransform, self.verticalScaleTransform, self.rect())

    def drawTrackerText(self, painter):
        if self.ruler:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            x = self.horizontalScaleTransform.toPlot(self.mousex)
            y = self.verticalScaleTransform.toPlot(float(self.height() - self.mousey))
            text = self.trackerFormatter(x, y)

            # compute tracker bounding rect
            painter.setPen(QtCore.Qt.black)
            rect = painter.boundingRect(QtCore.QRect(self.mousex, self.mousey, 0, 0), QtCore.Qt.AlignLeft, text)

            # small offset so that it does not touch the rulers
            rect.translate(4, -(rect.height() + 4))

            # avoid crossing the top and right borders
            dx = - max(rect.x() + rect.width() - self.width(), 0)
            dy = - min(rect.y(), 0)
            rect.translate(dx, dy)

            # avoid crossing the left and bottom borders
            dx = - min(rect.x(), 0)
            dy = - max(rect.y() + rect.height() - self.height(), 0)
            rect.translate(dx, dy)

            # draw a white background
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtCore.Qt.white)
            painter.drawRect(rect)

            painter.setPen(QtCore.Qt.black)
            painter.drawText(rect, QtCore.Qt.AlignLeft, text)

    def drawBackground(self, painter):
        if self.anyOpaqueItem:
            return

        self.grid.draw(painter, self.horizontalScaleTransform, self.verticalScaleTransform, self.rect())

    def drawBorder(self, painter):
        w = self.width()
        h = self.height()
        rectPath = QtGui.QPainterPath()
        rectPath.moveTo(0, 0)
        rectPath.lineTo(0, h - 1)
        rectPath.lineTo(w - 1, h - 1)
        rectPath.lineTo(w - 1, 0)
        rectPath.closeSubpath()

        painter.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.gray)))
        painter.drawPath(rectPath)

    def drawRuler(self, painter):
        if self.ruler:
            w = self.width()
            h = self.height()
            painter.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.black)))
            painter.drawLine(self.mousex, 0, self.mousex, h)
            painter.drawLine(0, self.mousey, w, self.mousey)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()
        self.mousex = event.x()
        self.mousey = event.y()
        self.ruler = True
        # ask for update so the the ruler is actually painted
        self.update()

    def mouseReleaseEvent(self, event):
        self.ruler = False
        # ask for update so the the ruler is actually erased
        self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.mousex = event.x()
            self.mousey = event.y()
            self.update()

    def setGrid(self, xMajorTick, xMinorTick, yMajorTick, yMinorTick):
        self.grid.setGrid(xMajorTick, xMinorTick, yMajorTick, yMinorTick)
