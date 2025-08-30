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

from PyQt5.QtQuick import QQuickItem

class TileLayout(QQuickItem):

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setFlag(QQuickItem.ItemHasContents, False)

        self.widthChanged.connect(self.updatePolish)
        self.heightChanged.connect(self.updatePolish)

    def itemChange(self, change, value):
        if (change == QQuickItem.ItemChildAddedChange
          or change == QQuickItem.ItemChildRemovedChange):
            self.polish()
    
        return super().itemChange(change, value)

    def componentComplete(self):
        self.polish()
        return super().componentComplete()
    
    def movePrevious(self, index):
        # move an item to the previous position in the layout
        if index > 0:
            children = self.childItems()
            item = children[index]
            item.stackBefore(children[index - 1])
            self.polish()
    
    def moveNext(self, index):
        # move an item to the next position in the layout
        children = self.childItems()
        if index < len(children) - 1:
            item = children[index]
            item.stackAfter(children[index + 1])
            self.polish()

    def updatePolish(self):
        children = self.childItems()
        childrenCount = len(children)

        if childrenCount == 0:
            return super().updatePolish()

        rowCount = math.ceil(math.sqrt(childrenCount))
        columnCount = math.ceil(childrenCount/rowCount)

        # the square root produces overestimated results
        # reduce to the smallest count
        m = 0
        n = 0
        while True:
            m += 1
            if (rowCount-m)*(columnCount-n) < childrenCount:
                m -= 1
                break
            n += 1
            if (rowCount-m)*(columnCount-n) < childrenCount:
                n -= 1
                break

        rowCount -= m
        columnCount -= n

        # produce a dictionary: key = line index, value = column count
        lines = {rowIndex: columnCount for rowIndex in range(rowCount)}

        # split the overflow over the lines
        overflow = rowCount*columnCount - childrenCount
        while overflow > 0:
            for i in range(rowCount):
                lines[i] = lines[i] - 1
                overflow -= 1
                if overflow == 0:
                    break

        rowHeight = self.height()//rowCount

        # now iterate over the items
        i = 0
        for rowIndex in lines.keys():
            columnCount = lines[rowIndex]
            columnWidth = self.width()//columnCount
            for columnIndex in range(columnCount):
                item = self.childItems()[i]
                x = columnIndex*columnWidth
                y = rowIndex*rowHeight

                item.setWidth(columnWidth)
                item.setHeight(rowHeight)
                item.setX(x)
                item.setY(y)

                i += 1

        return super().updatePolish()

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
