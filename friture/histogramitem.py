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

from PyQt5 import QtCore, Qt, QtGui
from numpy import array
import numpy as np

class HistogramItem:

    def __init__(self, *args):

        self.__color = Qt.QColor()

        self.cached_bar_width = 1
        self.canvas_height = 2
        self.canvas_width = 2
        self.need_transform = False
        self.fl = [0.]
        self.fh = [0.]
        self.fc = ["0"]  # center frequencies
        self.y = array([0.])
        self.i = [0]

        self.pixmaps = [QtGui.QPixmap()]
        self.max_label_pix_h_width = 0
        self.max_label_pix_v_width = 0
        self.pix_h_widths = 0
        self.pix_v_widths = 0
        self.pix_h_heights = 0
        self.pix_v_heights = 0
        self.h_pixmaps = [[QtGui.QPixmap(), QtGui.QPixmap()]]
        self.v_pixmaps = [[QtGui.QPixmap(), QtGui.QPixmap()]]

    def setData(self, fl, fh, fc, y):
        if len(self.y) != len(y):
            self.fl = fl
            self.fh = fh
            self.fc = fc
            self.need_transform = True
            self.update_labels_pixmap(self.fc)

        self.y = array(y)

    def set_color(self, color):
        if self.__color != color:
            self.__color = color

    def color(self):
        return self.__color

    def draw(self, painter, x_map, y_map, rect):
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
            self.x1 = np.round(x_map.toScreen(array(self.fl)))
            self.x2 = np.round(x_map.toScreen(array(self.fh))) - 1

            self.update_pixmap(self.x2[0] - self.x1[0], self.canvas_height)
            self.i = list(array(self.x2) - array(self.x1) - (self.cached_bar_width - 2))

            self.need_transform = False

        y = self.canvas_height - y_map.toScreen(self.y)

        for x1, x2, y2, i in zip(self.x1, self.x2, y, self.i):
            self.draw_bar(painter, x1, y2, i)

        w = self.x2[0] - self.x1[0]

        if self.max_label_pix_h_width <= w:  # try to draw the frequency labels horizontally
            self.draw_labels(painter, y, self.pix_h_widths, self.pix_h_heights, self.h_pixmaps)
        elif self.max_label_pix_v_width <= w:  # try to draw the frequency labels vertically
            self.draw_labels(painter, y, self.pix_v_widths, self.pix_v_heights, self.v_pixmaps)

    def draw_labels(self, painter, y, pix_widths, pix_heights, pixmaps):
        x = (self.x1 + self.x2) / 2 - pix_widths / 2  # center

        Dy = 6
        y += Dy  # some margin between top of the bar and text

        h_bound = 3
        y = (y >= h_bound) * y + (y < h_bound) * h_bound

        mask = y + pix_heights >= self.canvas_height - 1
        y = mask * (self.canvas_height - h_bound - pix_heights) + (~mask) * y
        ps = mask * 1 + (~mask) * 0

        for x1, y2, p, pixmap in zip(x, y, ps, pixmaps):
            painter.drawPixmap(x1, y2, pixmap[p])

    def draw_bar(self, painter, left, top, i):
        painter.drawPixmap(int(left), int(top), self.pixmaps[int(i)])

    # For a dramatic speedup, the bars are cached instead of drawn from scratch each time
    def update_pixmap(self, width, height):
        self.cached_bar_width = width

        color = QtGui.QColor(self.color())

        self.pixmaps = []
        for w in range(int(width) - 2, int(width) + 3):
            pixmap = QtGui.QPixmap(w + 1, height + 1)
            pixmap.fill(color)
            painter = QtGui.QPainter(pixmap)
            if width > 3:
                self.draw_bar_decoration(painter, w, height)
            self.pixmaps += [pixmap]

    def draw_bar_decoration(self, painter, width, height):
        color = QtGui.QColor(self.color())
        factor = 125
        light = color.lighter(factor)
        dark = color.darker(factor)

        painter.setBrush(Qt.Qt.NoBrush)

        top = 0
        bottom = height
        left = 0
        right = width - 1

        # horizontal line
        painter.setPen(Qt.QPen(light, 2))
        painter.drawLine(1, top + 2, right + 1, top + 2)

        # horizontal line
        painter.setPen(Qt.QPen(dark, 2))
        painter.drawLine(1, bottom, right + 1, bottom)

        # vertical line
        painter.setPen(Qt.QPen(light, 1))
        painter.drawLine(0, top + 1, 0, bottom)
        painter.drawLine(1, top + 2, 1, bottom - 1)

        # vertical line
        painter.setPen(Qt.QPen(dark, 1))
        painter.drawLine(right + 1, top + 1, right + 1, bottom)
        painter.drawLine(right, top + 2, right, bottom - 1)

    # For a dramatic speedup, the frequency labels are cached
    # instead of drawn from scratch each time
    def update_labels_pixmap(self, freq_list):
        labels_pixmaps_h_black = []
        labels_pixmaps_h_white = []
        labels_pixmaps_v_black = []
        labels_pixmaps_v_white = []

        w = h = 1
        test_pixmap = QtGui.QPixmap(w, h)
        test_pixmap.fill()
        test_painter = QtGui.QPainter(test_pixmap)
        f_rect = QtCore.QRectF(0, 0, w, h)

        transparent_color = QtGui.QColor(0, 0, 0, 0)

        for f in freq_list:
            # first, find the right pixmap size
            boundary_rect = test_painter.boundingRect(f_rect, Qt.Qt.AlignLeft, f)

            # second, create the pixmap with the right size
            pixmap = QtGui.QPixmap(boundary_rect.width(), boundary_rect.height())
            pixmap.fill(transparent_color)  # transparent background
            painter = QtGui.QPainter(pixmap)
            painter.setPen(QtCore.Qt.black)
            painter.drawText(boundary_rect, Qt.Qt.AlignLeft, f)
            labels_pixmaps_h_black += [pixmap]

            pixmap = QtGui.QPixmap(boundary_rect.width(), boundary_rect.height())
            pixmap.fill(transparent_color)  # transparent background
            painter = QtGui.QPainter(pixmap)
            painter.setPen(QtCore.Qt.white)
            painter.drawText(boundary_rect, Qt.Qt.AlignLeft, f)
            labels_pixmaps_h_white += [pixmap]

        angle = -90
        for pix in labels_pixmaps_h_black:
            pixmap = QtGui.QPixmap(pix.height(), pix.width())
            pixmap.fill(transparent_color)  # transparent background
            painter = QtGui.QPainter(pixmap)
            painter.rotate(angle)
            painter.drawPixmap(-pix.width(), 0, pix)
            labels_pixmaps_v_black += [pixmap]

        for pix in labels_pixmaps_h_white:
            pixmap = QtGui.QPixmap(pix.height(), pix.width())
            pixmap.fill(transparent_color)  # transparent background
            painter = QtGui.QPainter(pixmap)
            painter.rotate(angle)
            painter.drawPixmap(-pix.width(), 0, pix)
            labels_pixmaps_v_white += [pixmap]

        test_painter.end()  # manually ends painting to satisfy Qt

        self.pix_h_widths = array([pix.width() for pix in labels_pixmaps_h_white])
        self.max_label_pix_h_width = max(self.pix_h_widths)
        self.pix_h_heights = array([pix.height() for pix in labels_pixmaps_h_white])

        self.pix_v_widths = array([pix.width() for pix in labels_pixmaps_v_white])
        self.max_label_pix_v_width = max(self.pix_v_widths)
        self.pix_v_heights = array([pix.height() for pix in labels_pixmaps_v_white])

        self.h_pixmaps = [[pix_white, pix_black] for pix_white, pix_black in zip(labels_pixmaps_h_white,
                                                                                 labels_pixmaps_h_black)]

        self.v_pixmaps = [[pix_white, pix_black] for pix_white, pix_black in zip(labels_pixmaps_v_white,
                                                                                 labels_pixmaps_v_black)]
