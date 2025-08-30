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

import logging

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow
from friture.defaults import DEFAULT_DOCKS
from friture.dock import Dock
from friture.tilelayout import TileLayout

from typing import Dict, List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from friture.analyzer import Friture


class DockManager(QtCore.QObject):

    def __init__(self, parent: 'Friture', dock_layout: TileLayout) -> None:
        super().__init__(parent)
        self._parent = parent

        self.logger = logging.getLogger(__name__)

        # the parent must of the QMainWindow so that docks are created as children of it
        assert isinstance(parent, QMainWindow)

        self.docks: List[Dock] = []
        self.last_settings: Dict[int, QtCore.QSettings] = {}
        self.last_widget_stack: List[int] = []

        self.dock_layout = dock_layout

    # slot
    def new_dock(self) -> None:
        # the dock objectName is unique
        docknames = [dock.objectName() for dock in self.docks]
        dockindexes = [int(str(name).partition(' ')[-1]) for name in docknames]
        if len(dockindexes) == 0:
            index = 1
        else:
            index = max(dockindexes) + 1
        name = "Dock %d" % index

        widget_id: Optional[int] = None
        settings: Optional[QtCore.QSettings] = None
        if self.last_widget_stack:
            widget_id = self.last_widget_stack.pop()
            settings = self.last_settings.get(widget_id)

        new_dock = Dock(self._parent, name, self._parent.qml_engine, widget_id)
        if settings is not None:
            new_dock.restoreState(settings)

        self.docks += [new_dock]

    # slot
    def close_dock(self, dock: Dock) -> None:
        settings = QtCore.QSettings()
        dock.saveState(settings)
        assert dock.widgetId is not None # true but mypy can't prove it
        self.last_settings[dock.widgetId] = settings
        self.last_widget_stack.append(dock.widgetId)

        self.docks.remove(dock)
        dock.cleanup()
    
    def movePrevious(self, dock):
        i = self.docks.index(dock)
        if i > 0:
            self.dock_layout.movePrevious(i)
            self.docks.insert(i-1, self.docks.pop(i))

    def moveNext(self, dock):
        i = self.docks.index(dock)
        if i < len(self.docks) - 1:
            self.dock_layout.moveNext(i)
            self.docks.insert(i+1, self.docks.pop(i))

    def saveState(self, settings):
        docknames = [dock.objectName() for dock in self.docks]
        settings.setValue("dockNames", docknames)
        for dock in self.docks:
            settings.beginGroup(dock.objectName())
            dock.saveState(settings)
            settings.endGroup()

        settings.setValue("widgetIdStack", self.last_widget_stack)
        settings.beginGroup("lastSettings")
        for widgetId, widgetSettings in self.last_settings.items():
            settings.beginGroup(str(widgetId))
            for key in widgetSettings.allKeys():
                settings.setValue(key, widgetSettings.value(key))
            settings.endGroup()
        settings.endGroup()

    def restoreState(self, settings):
        if settings.contains("dockNames"):
            docknames = settings.value("dockNames", [])
            # list of docks
            self.docks = []
            for name in docknames:
                settings.beginGroup(name)
                widgetId = settings.value("type", 0, type=int)
                dock = Dock(self.parent(), name, self.parent().qml_engine, widgetId)
                dock.restoreState(settings)
                settings.endGroup()
                self.docks.append(dock)
        else:
            self.logger.info("First launch, display a default set of docks")
            self.docks = [Dock(self.parent(), "Dock %d" % (i), self.parent().qml_engine, widgetId=widget_type) for i, widget_type in enumerate(DEFAULT_DOCKS)]

        # Ugh it seems QSettings encodes an empty stack the same as None, and
        # that counts as being set so it doesn't get the default, and hence the
        # `or []` to correctly read back an empty stack.
        self.last_widget_stack = settings.value("widgetIdStack", []) or []
        settings.beginGroup("lastSettings")
        for strId in settings.childGroups():
            settings.beginGroup(strId)
            widgetSettings = QtCore.QSettings()
            for key in settings.allKeys():
                widgetSettings.setValue(key, settings.value(key))
            self.last_settings[int(strId)] = widgetSettings
            settings.endGroup()
        settings.endGroup()

    def canvasUpdate(self):
        if self._parent.isVisible():
            for dock in self.docks:
                dock.canvasUpdate()

    def pause(self):
        for dock in self.docks:
            try:
                dock.pause()
            except AttributeError:
                pass

    def restart(self):
        for dock in self.docks:
            try:
                dock.restart()
            except AttributeError:
                pass
