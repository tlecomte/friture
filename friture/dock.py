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
from PyQt5.QtQuick import QQuickView, QQuickItem # type: ignore
from PyQt5.QtQml import QQmlComponent
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtWidgets import QWidget

from friture.qml_tools import component_raise_if_error, qml_url
from friture.widgetdict import getWidgetById, widgetIds
from friture.controlbar_viewmodel import ControlBarViewModel

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

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        self.qml_engine = qml_engine

        self.controlbar_viewmodel = ControlBarViewModel(self)

        self.controlbar_viewmodel.indexChanged.connect(self.indexChanged)
        self.controlbar_viewmodel.settingsClicked.connect(lambda: self.settings_slot(False))
        self.controlbar_viewmodel.movePreviousClicked.connect(self.movePrevious)
        self.controlbar_viewmodel.moveNextClicked.connect(self.moveNext)
        self.controlbar_viewmodel.closeClicked.connect(self.closeClicked)

        self.dockQuickWidget = QQuickWidget(self.qml_engine, self)
        self.dockQuickWidget.setObjectName("dockQuickWidget")
        self.dockQuickWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.dockQuickWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.dockQuickWidget.setSource(qml_url("Dock.qml"))
        self.vbox.addWidget(self.dockQuickWidget)

        dock_root = self.dockQuickWidget.rootObject()
        
        initialProperties = {"viewModel": self.controlbar_viewmodel}
        component = QQmlComponent(self.qml_engine)
        component.loadUrl(qml_url("ControlBar.qml"))

        component_raise_if_error(component)

        controlbar_context = self.qml_engine.rootContext()
        control_bar_qml = component.createWithInitialProperties(initialProperties, controlbar_context)
        control_bar_qml.setParent(self.qml_engine)

        control_bar_container = dock_root.findChild(QObject, "control_bar_container")
        control_bar_qml.setParentItem(control_bar_container) # type: ignore
 
        self.audio_widget_container = dock_root.findChild(QObject, "audio_widget_container")

        self.widgetId: Optional[int] = None
        self.audiowidget: Optional[QObject] = None
        self.audio_widget_qml: Optional[QQuickItem] = None

        if widgetId is None:
            widgetId = widgetIds()[0]

        self.widget_select(widgetId)

    # note that by default the closeEvent is accepted, no need to do it explicitely
    def closeEvent(self, event):
        self.dockmanager.close_dock(self)

        if self.audio_widget_qml is not None:
            self.audio_widget_qml.setParentItem(None) # type: ignore
            self.audio_widget_qml.deleteLater()
            self.audio_widget_qml = None

        if self.audiowidget is not None:
            if hasattr(self.audiowidget, 'cleanup'):
                self.audiowidget.cleanup()
            self.audiowidget.deleteLater()
            self.audiowidget = None

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
        
        if self.audio_widget_qml is not None:
            self.audio_widget_qml.setParentItem(None) # type: ignore
            self.audio_widget_qml.deleteLater()
            self.audio_widget_qml = None

        if self.audiowidget is not None:
            settings = QtCore.QSettings()
            self.audiowidget.saveState(settings) # type: ignore
            assert self.widgetId is not None
            self.dockmanager.last_settings[self.widgetId] = settings
            if hasattr(self.audiowidget, 'cleanup'):
                self.audiowidget.cleanup()
            self.audiowidget.deleteLater()
            self.audiowidget = None

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

        initialProperties = {
            "fixedFont": QFontDatabase.systemFont(QFontDatabase.FixedFont).family(),
            "viewModel": self.audiowidget.view_model(), # type: ignore
        }

        # audiowidget is duck typed for this:
        self.audiowidget.set_buffer(self.audiobuffer) # type: ignore
        self.audiobuffer.new_data_available.connect(
            self.audiowidget.handle_new_data) # type: ignore
        if widgetId in self.dockmanager.last_settings:
            self.audiowidget.restoreState( # type: ignore
                self.dockmanager.last_settings[widgetId])

        component = QQmlComponent(self.qml_engine)
        component.loadUrl(qml_url(self.audiowidget.qml_file_name())) # type: ignore

        component_raise_if_error(component)
        component.statusChanged.connect(self.on_status_changed)

        qml_context = self.qml_engine.rootContext()
        self.audio_widget_qml = component.createWithInitialProperties(initialProperties, qml_context) # type: ignore
        self.audio_widget_qml.setParent(self.qml_engine) # type: ignore
        self.audio_widget_qml.setParentItem(self.audio_widget_container) # type: ignore
        self.audio_widget_qml.setProperty("anchors.fill", self.audio_widget_container) # type: ignore

        index = widgetIds().index(widgetId)
        self.controlbar_viewmodel.setCurrentIndex(index)

    def on_status_changed(self, status):
        if status == QQmlComponent.Error:
            for error in self.audio_widget_qml.errors():
                self.logger.error("QML error: " + error.toString())

    def canvasUpdate(self):
        if self.audiowidget is not None and self.isVisible():
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
