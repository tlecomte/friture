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

from PyQt4 import QtGui

from friture.plotting.titleWidget import VerticalTitleWidget, HorizontalTitleWidget, ColorTitleWidget
from friture.plotting.scaleBar import VerticalScaleBar, HorizontalScaleBar, ColorScaleBar

# A layout widget containing:
# - a title
# - a scale bar with a baseline, ticks and tick labels
# The logic of the placement of scale min/max and ticks belongs to another class
class VerticalScaleWidget(QtGui.QWidget):
    def __init__(self, parent, transformation, scaleDivision, logger=None):
        super(VerticalScaleWidget, self).__init__()

        self.titleWidget = VerticalTitleWidget("Scale Widget Title", self)
        self.scaleBar = VerticalScaleBar(self, transformation, scaleDivision)

        plotLayout = QtGui.QGridLayout()
        plotLayout.setSpacing(0)
        plotLayout.setContentsMargins(0, 0, 0, 0)
        plotLayout.addWidget(self.titleWidget, 0, 0)
        plotLayout.addWidget(self.scaleBar, 0, 1)

        self.setLayout(plotLayout)

    def setTitle(self, title):
        self.titleWidget.setTitle(title)

    def setScaleProperties(self, transformation, scaleDivision):
        self.scaleBar.set_scale_properties(transformation, scaleDivision)

    def spacingBorders(self):
        return self.scaleBar.spacingBorders()


class HorizontalScaleWidget(QtGui.QWidget):
    def __init__(self, parent, transformation, scaleDivision, logger=None):
        super(HorizontalScaleWidget, self).__init__()

        self.titleWidget = HorizontalTitleWidget("Scale Widget Title", self)
        self.scaleBar = HorizontalScaleBar(self, transformation, scaleDivision)

        plotLayout = QtGui.QGridLayout()
        plotLayout.setSpacing(0)
        plotLayout.setContentsMargins(0, 0, 0, 0)
        plotLayout.addWidget(self.scaleBar, 0, 0)
        plotLayout.addWidget(self.titleWidget, 1, 0)

        self.setLayout(plotLayout)

    def setTitle(self, title):
        self.titleWidget.setTitle(title)

    def setScaleProperties(self, transformation, scaleDivision):
        self.scaleBar.set_scale_properties(transformation, scaleDivision)

    def spacingBorders(self):
        return self.scaleBar.spacingBorders()


class ColorScaleWidget(QtGui.QWidget):
    def __init__(self, parent, transformation, scaleDivision, logger=None):
        super(ColorScaleWidget, self).__init__()

        self.titleWidget = ColorTitleWidget("Scale Widget Title", self)
        self.scaleBar = ColorScaleBar(self, transformation, scaleDivision)

        plotLayout = QtGui.QGridLayout()
        plotLayout.setSpacing(0)
        plotLayout.setContentsMargins(0, 0, 0, 0)
        plotLayout.addWidget(self.scaleBar, 0, 0)
        plotLayout.addWidget(self.titleWidget, 0, 1)

        self.setLayout(plotLayout)

    def setTitle(self, title):
        self.titleWidget.setTitle(title)

    def setScaleProperties(self, transformation, scaleDivision):
        self.scaleBar.set_scale_properties(transformation, scaleDivision)

    def spacingBorders(self):
        return self.scaleBar.spacingBorders()
