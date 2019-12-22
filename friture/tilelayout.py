#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2017 Timothée Lecomte

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

import math
from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtWidgets import QLayout, QSizePolicy


class TileLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(TileLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        # expand in both directions
        return Qt.Orientations(Qt.Horizontal | Qt.Vertical)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(TileLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margin, _, _, _ = self.getContentsMargins()

        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        if len(self.itemList) == 0:
            return rect.height()

        rowCount = math.ceil(math.sqrt(len(self.itemList)))
        columnCount = math.ceil(len(self.itemList)/rowCount)

        # the square root produces overestimated results
        # reduce to the smallest count
        m = 0
        n = 0
        while True:
            m += 1
            if (rowCount-m)*(columnCount-n) < len(self.itemList):
                m -= 1
                break
            n += 1
            if (rowCount-m)*(columnCount-n) < len(self.itemList):
                n -= 1
                break

        rowCount -= m
        columnCount -= n

        # produce a dictionary: key = line index, value = column count
        lines = {rowIndex: columnCount for rowIndex in range(rowCount)}

        # split the overflow over the lines
        overflow = rowCount*columnCount - len(self.itemList)
        while overflow > 0:
            for i in range(rowCount):
                lines[i] = lines[i] - 1
                overflow -= 1
                if overflow == 0:
                    break

        rowHeight = rect.height()//rowCount

        # now iterate over the items
        i = 0
        for rowIndex in lines.keys():
            columnCount = lines[rowIndex]
            columnWidth = rect.width()//columnCount
            for columnIndex in range(columnCount):
                item = self.itemList[i]
                x = rect.x() + columnIndex*columnWidth
                y = rect.y() + rowIndex*rowHeight

                if not testOnly:
                    item.setGeometry(QRect(QPoint(x, y), QSize(columnWidth, rowHeight)))

                i += 1

        return rect.height()

# example:
# 1 => X
# 2 => X,X horizontal or vertical depending on which brings the result closer to the golden ratio for each widget
# 3 => X,X,X in one row or column or multiple, depending on which brings the result closer to the golden ratio

# Idea 1: dynamic grid layout
# Idea 2: vertical layout containing horizontal layout
# Idea 3: 12x12 grid layout

# 12 = 1*12 = 2*6 = 3*4 = 4*3 = 6*2 = 12*1

# Example: 5 widgets in 1000x800

# 5/2 = 2.5
# 5//2 = 2
# 5//2 + 1 = 3

# if divisible by 2: "simple"
# if not, one row/column will have one more item

# AR = parent aspect ratio 1366/768 = 1.78

# G = golden ratio = 1.62

# how to decide how many rows we need?
# -> a threshold based on G
