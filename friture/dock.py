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
from friture.widgetdict import getWidgetById, widgetIds
from friture.controlbar import ControlBar


class Dock(QtWidgets.QWidget):

    def __init__(self, parent, name, widgetId=None):
        super().__init__(parent)

        self.dockmanager = parent.dockmanager
        self.audiobuffer = parent.audiobuffer

        self.setObjectName(name)

        self.control_bar = ControlBar(self)

        self.control_bar.combobox_select.activated.connect(self.indexChanged)
        self.control_bar.settings_button.clicked.connect(self.settings_slot)
        self.control_bar.close_button.clicked.connect(self.closeClicked)

        #self.dockwidget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.control_bar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # self.dockwidget.setLayout(self.layout)

        # self.setWidget(self.dockwidget)

        self.audiowidget = None
        self.widget_select(widgetId)

    # note that by default the closeEvent is accepted, no need to do it explicitely
    def closeEvent(self, event):
        self.dockmanager.close_dock(self)

    def closeClicked(self, checked):
        self.close()

    # slot
    def indexChanged(self, index):
        if index > len(widgetIds()):
            index = widgetIds()[0]

        self.widget_select(widgetIds()[index])

    # slot
    def widget_select(self, widgetId):
        if self.audiowidget is not None:
            self.audiowidget.close()
            self.audiowidget.deleteLater()

        if widgetId not in widgetIds():
            widgetId = widgetIds()[0]

        self.widgetId = widgetId
        self.audiowidget = getWidgetById(widgetId)["Class"](self)
        self.audiowidget.set_buffer(self.audiobuffer)
        self.audiobuffer.new_data_available.connect(self.audiowidget.handle_new_data)

        self.layout.addWidget(self.audiowidget)

        index = widgetIds().index(widgetId)
        self.control_bar.combobox_select.setCurrentIndex(index)

    def canvasUpdate(self):
        if self.audiowidget is not None:
            self.audiowidget.canvasUpdate()

    def pause(self):
        if self.audiowidget is not None:
            self.audiowidget.pause()

    def restart(self):
        if self.audiowidget is not None:
            self.audiowidget.restart()

    # slot
    def settings_slot(self, checked):
        self.audiowidget.settings_called(checked)

    # method
    def saveState(self, settings):
        settings.setValue("type", self.widgetId)
        self.audiowidget.saveState(settings)

    # method
    def restoreState(self, settings):
        widgetId = settings.value("type", 0, type=int)
        self.widget_select(widgetId)
        self.audiowidget.restoreState(settings)
