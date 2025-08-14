#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

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

from PyQt5 import QtCore

class Delay_Estimator_View_Model(QtCore.QObject):
    delayChanged = QtCore.pyqtSignal(str)
    correlationChanged = QtCore.pyqtSignal(str)
    polarityChanged = QtCore.pyqtSignal(str)
    channelInfoChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._delay = ""
        self._correlation = ""
        self._polarity = ""
        self._channel_info = ""

    @QtCore.pyqtProperty(str, notify=delayChanged)
    def delay(self):
        return self._delay

    @delay.setter # type: ignore
    def delay(self, value):
        if self._delay != value:
            self._delay = value
            self.delayChanged.emit(value)

    @QtCore.pyqtProperty(str, notify=correlationChanged)
    def correlation(self):
        return self._correlation

    @correlation.setter # type: ignore
    def correlation(self, value):
        if self._correlation != value:
            self._correlation = value
            self.correlationChanged.emit(value)

    @QtCore.pyqtProperty(str, notify=polarityChanged)
    def polarity(self):
        return self._polarity

    @polarity.setter # type: ignore
    def polarity(self, value):
        if self._polarity != value:
            self._polarity = value
            self.polarityChanged.emit(value)

    @QtCore.pyqtProperty(str, notify=channelInfoChanged)
    def channel_info(self):
        return self._channel_info

    @channel_info.setter # type: ignore
    def channel_info(self, value):
        if self._channel_info != value:
            self._channel_info = value
            self.channelInfoChanged.emit(value)
