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


class Dock(QtWidgets.QDockWidget):

    def __init__(self, parent, name, widget_type=0):
        super().__init__(name, parent)

        self.setObjectName(name)

        self.control_bar = ControlBar(self)

        self.control_bar.combobox_select.activated.connect(self.widget_select)
        self.control_bar.settings_button.clicked.connect(self.settings_slot)

        self.dockwidget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout(self.dockwidget)
        self.layout.addWidget(self.control_bar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.dockwidget.setLayout(self.layout)

        self.setWidget(self.dockwidget)

        self.audiowidget = None
        self.widget_select(widget_type)

    # note that by default the closeEvent is accepted, no need to do it explicitely
    def closeEvent(self, event):
        self.parent().dockmanager.close_dock(self)

    # slot
    def widget_select(self, item):
        if self.audiowidget is not None:
            self.audiowidget.close()
            self.audiowidget.deleteLater()

        if item not in widgetIds():
            item = widgetIds()[0]

        self.type = item
        self.audiowidget = getWidgetById(item)["Class"](self)
        self.audiowidget.set_buffer(self.parent().audiobuffer)
        self.parent().audiobuffer.new_data_available.connect(self.audiowidget.handle_new_data)

        self.layout.addWidget(self.audiowidget)

        self.control_bar.combobox_select.setCurrentIndex(item)

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
        settings.setValue("type", self.type)
        self.audiowidget.saveState(settings)

    # method
    def restoreState(self, settings):
        widget_type = settings.value("type", 0, type=int)
        self.widget_select(widget_type)
        self.audiowidget.restoreState(settings)
