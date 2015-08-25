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


class CanvasBackground:

    def __init__(self, *args):
        self.canvas_width = 2
        self.canvas_height = 2

        self.need_redraw = False

        self.cache_pixmap = QtGui.QPixmap()

    def drawToCache(self, painter, rect):
        w = rect.width()
        h = rect.height()

        self.cache_pixmap = QtGui.QPixmap(w, h)

        painter = QtGui.QPainter(self.cache_pixmap)
        self.directDraw(painter, rect)

    def directDraw(self, painter, rect):
        # verical gradient from top to bottom
        gradient = QtGui.QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0, QtGui.QColor("#E0E0E0"))
        gradient.setColorAt(0.5, QtCore.Qt.white)
        painter.fillRect(rect, gradient)

    def draw(self, painter, rect):
        # update the cache according to possibly new canvas dimensions
        h = rect.height()
        w = rect.width()

        if w != self.canvas_width:
            self.canvas_width = w
            self.need_redraw = True

        if h != self.canvas_height:
            self.canvas_height = h
            self.need_redraw = True

        if self.need_redraw:
            self.drawToCache(painter, rect)
            self.need_redraw = False

        painter.drawPixmap(0, 0, self.cache_pixmap)
