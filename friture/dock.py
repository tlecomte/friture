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

from inspect import signature

from PyQt5 import QtCore, QtWidgets
from friture.widgetdict import getWidgetById, widgetIds
from friture.controlbar import ControlBar

from typing import Dict, List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from friture.analyzer import Friture
    from friture.dockmanager import DockManager
    from friture.playback.control import PlaybackControlWidget
    from PyQt5.QtQml import QQmlEngine


class Dock(QtWidgets.QWidget):

    def __init__(
        self,
        parent: 'Friture',
        name: str,
        qml_engine: 'QQmlEngine',
        widgetId: Optional[int]=None
    ) -> None:
        super().__init__(parent)

        self.dockmanager: 'DockManager' = parent.dockmanager
        self.audiobuffer = parent.audiobuffer
        self.playback_widget: 'PlaybackControlWidget' = parent.playback_widget

        self.setObjectName(name)

        self.control_bar = ControlBar(self)

        self.control_bar.combobox_select.activated.connect(self.indexChanged)
        self.control_bar.settings_button.clicked.connect(self.settings_slot)
        self.control_bar.close_button.clicked.connect(self.closeClicked)

        #self.dockwidget = QtWidgets.QWidget(self)
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addWidget(self.control_bar)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        # self.dockwidget.setLayout(self.vbox)

        # self.setWidget(self.dockwidget)

        self.widgetId: Optional[int] = None
        self.audiowidget: Optional[QtWidgets.QWidget] = None
        self.qml_engine = qml_engine

        if widgetId is None:
            widgetId = widgetIds()[0]

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
    def widget_select(self, widgetId: int) -> None:
        if self.widgetId == widgetId:
            return

        if self.audiowidget is not None:
            settings = QtCore.QSettings()
            self.audiowidget.saveState(settings) # type: ignore
            assert self.widgetId is not None
            self.dockmanager.last_settings[self.widgetId] = settings

            self.audiowidget.close()
            self.audiowidget.deleteLater()

        if widgetId not in widgetIds():
            widgetId = widgetIds()[0]

        self.widgetId = widgetId

        constructor = getWidgetById(widgetId)["Class"]
        if len(signature(constructor).parameters) == 2:
            self.audiowidget = constructor(self, self.qml_engine)
        else:
            self.audiowidget = constructor(self)
        assert self.audiowidget is not None # mypy can't prove this :(

        if hasattr(self.audiowidget, 'connect_time_selected'):
            self.audiowidget.connect_time_selected(
                self.playback_widget.on_time_selected)

        # audiowidget is duck typed for this:
        self.audiowidget.set_buffer(self.audiobuffer) # type: ignore
        self.audiobuffer.new_data_available.connect(
            self.audiowidget.handle_new_data) # type: ignore
        if widgetId in self.dockmanager.last_settings:
            self.audiowidget.restoreState( # type: ignore
                self.dockmanager.last_settings[widgetId])

        self.vbox.addWidget(self.audiowidget)

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
        self.audiowidget.restoreState(settings)
