#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

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

from PyQt5 import QtWidgets
from friture.levels import Levels_Widget
from friture.spectrum import Spectrum_Widget
from friture.spectrogram import Spectrogram_Widget
from friture.octavespectrum import OctaveSpectrum_Widget
from friture.scope import Scope_Widget
from friture.generator import Generator_Widget
from friture.delay_estimator import Delay_Estimator_Widget
from friture.longlevels import LongLevelWidget
from friture.controlbar import ControlBar
from friture.defaults import DEFAULT_CENTRAL_WIDGET


class CentralWidget(QtWidgets.QWidget):

    def __init__(self, parent, logger, name, widget_type=0):
        super().__init__(parent)

        self.setObjectName(name)

        self.logger = logger

        self.control_bar = ControlBar(self)

        self.control_bar.combobox_select.activated.connect(self.widget_select)
        self.control_bar.settings_button.clicked.connect(self.settings_slot)

        self.label = QtWidgets.QLabel(self)
        self.label.setText(" Central dock ")  # spaces before and after for nicer alignment
        self.control_bar.layout.insertWidget(0, self.label)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.control_bar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.audiowidget = None
        self.widget_select(widget_type)

    # slot
    def widget_select(self, item):
        if self.audiowidget is not None:
            self.audiowidget.close()
            self.audiowidget.deleteLater()

        self.type = item

        if item is 0:
            self.audiowidget = Levels_Widget(self, self.logger)
        elif item is 1:
            self.audiowidget = Scope_Widget(self, self.logger)
        elif item is 2:
            self.audiowidget = Spectrum_Widget(self, self.logger)
        elif item is 3:
            self.audiowidget = Spectrogram_Widget(self, self.parent().parent().audiobackend, self.logger)
        elif item is 4:
            self.audiowidget = OctaveSpectrum_Widget(self, self.logger)
        elif item is 5:
            self.audiowidget = Generator_Widget(self, self.parent().parent().audiobackend, self.logger)
        elif item is 6:
            self.audiowidget = Delay_Estimator_Widget(self, self.logger)
        elif item is 7:
            self.audiowidget = LongLevelWidget(self, self.logger)
        else:
            self.audiowidget = Levels_Widget(self, self.logger)

        self.audiowidget.set_buffer(self.parent().parent().audiobuffer)
        self.parent().parent().audiobuffer.new_data_available.connect(self.audiowidget.handle_new_data)

        self.layout.addWidget(self.audiowidget)

        self.control_bar.combobox_select.setCurrentIndex(item)

    def canvasUpdate(self):
        if self.audiowidget is not None:
            self.audiowidget.canvasUpdate()

    def pause(self):
        if self.audiowidget is not None:
            try:
                self.audiowidget.pause()
            except AttributeError:
                pass

    def restart(self):
        if self.audiowidget is not None:
            try:
                self.audiowidget.restart()
            except AttributeError:
                pass

    # slot
    def settings_slot(self, checked):
        self.audiowidget.settings_called(checked)

    # method
    def saveState(self, settings):
        settings.setValue("type", self.type)
        self.audiowidget.saveState(settings)

    # method
    def restoreState(self, settings):
        widget_type = settings.value("type", DEFAULT_CENTRAL_WIDGET)
        self.widget_select(widget_type)
        self.audiowidget.restoreState(settings)
