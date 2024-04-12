#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

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
from typing import Any

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QGridLayout, QSizePolicy, QWidget
from PyQt5.QtQml import QQmlEngine
from PyQt5.QtQuickWidgets import QQuickWidget

from friture.qml_tools import qml_url, raise_if_error
from friture.playback.player import Player

logger = logging.getLogger(__name__)

class PlaybackControlWidget(QWidget):
    recording_toggled = pyqtSignal()

    def __init__(self, parent: QWidget, engine: QQmlEngine, player: Player):
        super().__init__(parent)
        self.widget = QQuickWidget(engine, self)
        self.widget.statusChanged.connect(self.on_status_changed)
        self.widget.setResizeMode(QQuickWidget.SizeViewToRootObject)
        self.widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        self.widget.setClearColor(self.palette().color(QPalette.Window))
        self.widget.setSource(qml_url("playback/Control.qml"))
        raise_if_error(self.widget)

        layout = QGridLayout(self)
        layout.addWidget(self.widget)
        self.setLayout(layout)

        self.root: Any = self.widget.rootObject()
        self.root.stopClicked.connect(self.on_stopped)
        self.root.recordClicked.connect(self.on_record)
        self.root.playClicked.connect(self.on_played)

        self.player = player
        self.player.stopped.connect(self.on_playback_stopped)


    def start_recording(self) -> None:
        if not self.player.is_stopped():
            self.player.stop()
        self.root.showRecording()

    def stop_recording(self) -> None:
        self.root.showStopped()

    def on_status_changed(self, status: QQuickWidget.Status) -> None:
        if status == QQuickWidget.Error:
            for error in self.widget.errors():
                logger.error("QML error: " + error.toString())

    def on_stopped(self) -> None:
        if self.player.is_stopped():
            self.recording_toggled.emit()
        else:
            self.player.stop()

    def on_record(self) -> None:
        self.recording_toggled.emit()

    def on_played(self) -> None:
        self.player.play()

    def on_playback_stopped(self) -> None:
        self.root.showStopped()
