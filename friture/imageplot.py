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

import logging
from PyQt5 import QtWidgets
from PyQt5.QtQuickWidgets import QQuickWidget
from friture.qml_tools import qml_url, raise_if_error
from friture.spectrogram_data import Spectrogram_Data
from friture.spectrogram_item_data import SpectrogramImageData
from friture.store import GetStore
from friture.pitch_tracker import format_frequency

class ImagePlot(QQuickWidget):

    def __init__(self, parent, engine):
        super(ImagePlot, self).__init__(engine, parent)

        self.logger = logging.getLogger(__name__)

        store = GetStore()
        self._spectrogram_data = Spectrogram_Data(store)
        store._dock_states.append(self._spectrogram_data)
        state_id = len(store._dock_states) - 1

        self._spectrogram_item = SpectrogramImageData()
        self._spectrogram_data.add_plot_item(self._spectrogram_item)

        self._spectrogram_data.show_legend = False
        self._spectrogram_data.vertical_axis.name = "Frequency (Hz)"
        self._spectrogram_data.vertical_axis.setTrackerFormatter(format_frequency)
        self._spectrogram_data.horizontal_axis.name = "Time (s)"
        self._spectrogram_data.horizontal_axis.setTrackerFormatter(lambda x: "%.2f s" % (x))
        self._spectrogram_data.color_axis.name = "PSD (dB A)"

        self._spectrogram_data.vertical_axis.setRange(20, 20000)
        self._spectrogram_data.horizontal_axis.setRange(0, 10)
        self._spectrogram_data.color_axis.setRange(-140, 0)
        self._spectrogram_data.show_color_axis = True

        self.statusChanged.connect(self.on_status_changed)
        self.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setSource(qml_url("ImagePlot.qml"))
        
        raise_if_error(self)

        self.rootObject().setProperty("stateId", state_id)

    def on_status_changed(self, status):
        if status == QQuickWidget.Error:
            for error in self.errors():
                self.logger.error("QML error: " + error.toString())

    def push(self, data, last_data_time):
        self._spectrogram_item.push(data, last_data_time)

    def spectrogram_screen_width(self):
        return self._spectrogram_item.screen_width()

    def spectrogram_screen_height(self):
        return self._spectrogram_item.screen_height()

    def draw(self):
        self._spectrogram_item.draw()

    def pause(self):
        self._spectrogram_item.pause()

    def restart(self):
        self._spectrogram_item.restart()

    def set_jitter(self, jitter_seconds: float) -> None:
        self._spectrogram_item.set_jitter(jitter_seconds)

    def setfreqscale(self, scale):        
        self._spectrogram_data.vertical_axis.setScale(scale)
        self._spectrogram_item.erase()

    def settimerange(self, timerange_seconds, dT_seconds):
        self._spectrogram_data.horizontal_axis.setRange(0, timerange_seconds)
        self._spectrogram_item.settimerange(timerange_seconds)

    def setfreqrange(self, minfreq, maxfreq):
        if minfreq > maxfreq:
            minfreq, maxfreq = maxfreq, minfreq

        self._spectrogram_data.vertical_axis.setRange(minfreq, maxfreq)

    def setspecrange(self, spec_min, spec_max):
        if spec_min > spec_max:
            spec_min, spec_max = spec_max, spec_min

        self._spectrogram_data.color_axis.setRange(spec_min, spec_max)

    def setweighting(self, weighting):
        if weighting == 0:
            title = "PSD (dB)"
        elif weighting == 1:
            title = "PSD (dB A)"
        elif weighting == 2:
            title = "PSD (dB B)"
        else:
            title = "PSD (dB C)"

        self._spectrogram_data.color_axis.name = title
