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

from PyQt5 import QtCore, QtGui
import numpy as np
from friture.plotting.canvasBackground import CanvasBackground


class Grid:

    def __init__(self, *args):
        self.canvas_width = 2
        self.canvas_height = 2

        self.need_transform = False

        self.cache_pixmap = QtGui.QPixmap()

        self.xMajorTick = np.array([])
        self.xMinorTick = np.array([])
        self.yMajorTick = np.array([])
        self.yMinorTick = np.array([])

        self.background = CanvasBackground()

    def setGrid(self, xMajorTick, xMinorTick, yMajorTick, yMinorTick):
        self.xMajorTick = xMajorTick
        self.xMinorTick = xMinorTick
        self.yMajorTick = yMajorTick
        self.yMinorTick = yMinorTick

        self.need_transform = True

    def drawToCache(self, painter, xMap, yMap, rect):
        w = rect.width()
        h = rect.height()

        xMajorTick = xMap.toScreen(self.xMajorTick)
        xMinorTick = xMap.toScreen(self.xMinorTick)
        yMajorTick = h - yMap.toScreen(self.yMajorTick)
        yMinorTick = h - yMap.toScreen(self.yMinorTick)

        self.cache_pixmap = QtGui.QPixmap(w, h)
        self.cache_pixmap.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(self.cache_pixmap)

        self.background.directDraw(painter, rect)

        painter.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.gray)))
        for x in xMajorTick:
            painter.drawLine(x, 0, x, h)

        painter.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.lightGray)))
        for x in xMinorTick:
            painter.drawLine(x, 0, x, h)

        painter.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.gray)))
        for y in yMajorTick:
            painter.drawLine(0, y, w, y)

        # given the usual aspect ratio of the canvas, the vertical minor ticks would make it look crowded
        # painter.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.lightGray)))
        # for y in yMinorTick:
        #    painter.drawLine(0, y, w, y)

    def draw(self, painter, xMap, yMap, rect):
        # update the cache according to possibly new canvas dimensions
        h = rect.height()
        w = rect.width()

        if w != self.canvas_width:
            self.canvas_width = w
            self.need_transform = True

        if h != self.canvas_height:
            self.canvas_height = h
            self.need_transform = True

        if self.need_transform:
            self.drawToCache(painter, xMap, yMap, rect)
            self.need_transform = False

        painter.drawPixmap(0, 0, self.cache_pixmap)
