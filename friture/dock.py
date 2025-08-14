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
from PyQt5.QtQuick import QQuickView # type: ignore
from PyQt5.QtGui import QFontDatabase, QWindow
from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtWidgets import QWidget

from friture.qml_tools import qml_url, raise_if_error
from friture.widgetdict import getWidgetById, widgetIds
from friture.controlbar import ControlBar

from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from friture.analyzer import Friture
    from friture.dockmanager import DockManager
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

        self.setObjectName(name)

        self.control_bar = ControlBar(self)

        self.control_bar.combobox_select.activated.connect(self.indexChanged)
        self.control_bar.settings_button.clicked.connect(self.settings_slot)
        self.control_bar.move_previous.clicked.connect(self.movePrevious)
        self.control_bar.move_next.clicked.connect(self.moveNext)
        self.control_bar.close_button.clicked.connect(self.closeClicked)

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.addWidget(self.control_bar)

        self.widgetId: Optional[int] = None
        self.audiowidget: Optional[QObject] = None
        self.quickWidget: Optional[QWidget] = None
        self.quickView: Optional[QQuickView] = None
        self.qml_engine = qml_engine

        if widgetId is None:
            widgetId = widgetIds()[0]

        self.widget_select(widgetId)

    # note that by default the closeEvent is accepted, no need to do it explicitely
    def closeEvent(self, event):
        self.dockmanager.close_dock(self)

    def closeClicked(self):
        self.close()

    def movePrevious(self):
        layout = self.parent().parent().centralLayout
        itemList = layout.itemList
        
        for i, item in enumerate(itemList):
            if item.widget() is self:
                if i > 0 and i < len(itemList):
                    itemList.insert(i-1, itemList.pop(i))
                    self.dockmanager.docks.insert(i-1, self.dockmanager.docks.pop(i))
                    layout.update()

                break

    def moveNext(self):
        layout = self.parent().parent().centralLayout
        itemList = layout.itemList
        
        for i, item in enumerate(itemList):
            if item.widget() is self:
                if i >= 0 and i < len(itemList)-1:
                    itemList.insert(i+1, itemList.pop(i))
                    self.dockmanager.docks.insert(i+1, self.dockmanager.docks.pop(i))
                    layout.update()
                break

    # slot
    def indexChanged(self, index):
        if index > len(widgetIds()):
            index = widgetIds()[0]

        self.widget_select(widgetIds()[index])

    # slot
    def widget_select(self, widgetId: int) -> None:
        if self.widgetId == widgetId:
            return

        if self.quickWidget is not None:
            self.quickWidget.close()
            self.quickWidget.deleteLater()

        if self.quickView is not None:
            self.quickView.close()
            self.quickView.deleteLater()

        if self.audiowidget is not None:
            settings = QtCore.QSettings()
            self.audiowidget.saveState(settings) # type: ignore
            assert self.widgetId is not None
            self.dockmanager.last_settings[self.widgetId] = settings
            self.audiowidget.deleteLater()

        if widgetId not in widgetIds():
            widgetId = widgetIds()[0]

        self.widgetId = widgetId

        widget_descriptor = getWidgetById(widgetId)

        constructor = widget_descriptor["Class"]
        if len(signature(constructor).parameters) == 2:
            self.audiowidget = constructor(self, self.qml_engine)
        else:
            self.audiowidget = constructor(self)
        assert self.audiowidget is not None # mypy can't prove this :(

        parent_window : QWindow = None # type: ignore
        self.quickView = QQuickView(self.qml_engine, parent_window)

        initialProperties = {
            "parent": self.quickView.contentItem(),
            "fixedFont": QFontDatabase.systemFont(QFontDatabase.FixedFont).family(),
            "viewModel": self.audiowidget.view_model() # type: ignore
        }

        self.quickView.setInitialProperties(initialProperties)
        self.quickView.setSource(qml_url(self.audiowidget.qml_file_name())) # type: ignore
        raise_if_error(self.quickView)
        self.quickView.statusChanged.connect(self.on_status_changed)
        self.quickView.setResizeMode(QQuickView.SizeRootObjectToView)

        self.quickWidget = QtWidgets.QWidget.createWindowContainer(self.quickView, self)
        self.quickWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # audiowidget is duck typed for this:
        self.audiowidget.set_buffer(self.audiobuffer) # type: ignore
        self.audiobuffer.new_data_available.connect(
            self.audiowidget.handle_new_data) # type: ignore
        if widgetId in self.dockmanager.last_settings:
            self.audiowidget.restoreState( # type: ignore
                self.dockmanager.last_settings[widgetId])

        self.vbox.addWidget(self.quickWidget)

        index = widgetIds().index(widgetId)
        self.control_bar.combobox_select.setCurrentIndex(index)

    def on_status_changed(self, status):
        if status == QQuickView.Error:
            for error in self.quickView.errors():
                self.logger.error("QML error: " + error.toString())

    def canvasUpdate(self):
        if self.audiowidget is not None and self.isVisible():
            self.audiowidget.canvasUpdate()

    def event(self, event):
        # workaround for loss of focus on macOS for QQuickView
        # https://bugreports.qt.io/browse/QTBUG-34414
        if event.type() == QEvent.WindowActivate:
            self.activateWindow()
            self.quickView.requestActivate()
    
        return super().event(event)

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
