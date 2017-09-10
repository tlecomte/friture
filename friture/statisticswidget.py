#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Timoth�e Lecomte

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

from PyQt5 import QtCore, QtWidgets
from friture.audiobackend import AudioBackend


class StatisticsWidget(QtWidgets.QWidget):

    def __init__(self, parent, timer):
        super().__init__(parent)

        self.setObjectName("tab_stats")

        self.stats_scrollarea = QtWidgets.QScrollArea(self)
        self.stats_scrollarea.setWidgetResizable(True)
        self.stats_scrollarea.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.stats_scrollarea.setObjectName("stats_scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget(self.stats_scrollarea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 87, 220))
        self.scrollAreaWidgetContents.setStyleSheet("""QWidget { background: white }""")
        self.scrollAreaWidgetContents.setObjectName("stats_scrollAreaWidgetContents")

        self.LabelStats = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.LabelStats.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.LabelStats.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard | QtCore.Qt.LinksAccessibleByMouse |
                                                QtCore.Qt.TextBrowserInteraction | QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.TextSelectableByMouse)
        self.LabelStats.setObjectName("LabelStats")

        self.stats_layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.stats_layout.setObjectName("stats_layout")
        self.stats_layout.addWidget(self.LabelStats)
        self.stats_scrollarea.setWidget(self.scrollAreaWidgetContents)

        self.tab_stats_layout = QtWidgets.QGridLayout(self)
        self.tab_stats_layout.addWidget(self.stats_scrollarea)

        timer.timeout.connect(self.stats_update)

    # method
    def stats_update(self):
        if not self.LabelStats.isVisible():
            return

        label = "Chunk #%d\n"\
            "Number of overflowed inputs (XRUNs): %d"\
            % (AudioBackend().chunk_number,
               AudioBackend().xruns)

        self.LabelStats.setText(label)
