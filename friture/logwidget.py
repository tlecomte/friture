#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Timothée Lecomte

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


class LogWidget(QtWidgets.QWidget):

    def __init__(self, parent, logger):
        super().__init__(parent)

        self.logger = logger

        self.setObjectName("tab_log")

        self.log_scrollarea = QtWidgets.QScrollArea(self)
        self.log_scrollarea.setWidgetResizable(True)
        self.log_scrollarea.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.log_scrollarea.setObjectName("log_scrollArea")

        self.log_scrollAreaWidgetContents = QtWidgets.QWidget(self.log_scrollarea)
        self.log_scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 87, 220))
        self.log_scrollAreaWidgetContents.setStyleSheet("""QWidget { background: white }""")
        self.log_scrollAreaWidgetContents.setObjectName("log_scrollAreaWidgetContents")
        self.log_scrollarea.setWidget(self.log_scrollAreaWidgetContents)

        self.LabelLog = QtWidgets.QLabel(self.log_scrollAreaWidgetContents)
        self.LabelLog.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.LabelLog.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard | QtCore.Qt.LinksAccessibleByMouse |
                                              QtCore.Qt.TextBrowserInteraction | QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.TextSelectableByMouse)
        self.LabelLog.setObjectName("LabelLog")

        self.log_layout = QtWidgets.QVBoxLayout(self.log_scrollAreaWidgetContents)
        self.log_layout.setObjectName("log_layout")
        self.log_layout.addWidget(self.LabelLog)

        self.tab_log_layout = QtWidgets.QGridLayout(self)
        self.tab_log_layout.addWidget(self.log_scrollarea)

        self.logger.logChanged.connect(self.log_changed)
        self.log_scrollarea.verticalScrollBar().rangeChanged.connect(self.log_scroll_range_changed)

    # slot
    # update the log widget with the new log content
    def log_changed(self):
        self.LabelLog.setText(self.logger.text())

    # slot
    # scroll the log widget so that the last line is visible
    def log_scroll_range_changed(self, scroll_min, scroll_max):
        scrollbar = self.log_scrollarea.verticalScrollBar()
        scrollbar.setValue(scroll_max)
