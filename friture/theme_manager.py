#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2026 Timothée Lecomte

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

from PyQt6 import QtCore
from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, Qt  # type: ignore
from PyQt6.QtGui import QGuiApplication  # type: ignore


class ThemeManager(QObject):
    """Manages application theme (light/dark/system) with persistence and system sync."""

    theme_changed = pyqtSignal(int)  # Qt.ColorScheme enum value

    def __init__(self, parent=None):
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        self._theme_preference = Qt.ColorScheme.Unknown  # Light, Dark, or Unknown (System)

        self._style_hints = QGuiApplication.styleHints()

        # Load saved preference
        self._load_settings()

        # Apply initial theme
        self._apply_theme_preference()

    def _load_settings(self):
        settings = QtCore.QSettings("Friture", "Friture")
        # 0 = System (Unknown), 1 = Light, 2 = Dark
        saved = settings.value("themePreference", 0, type=int)
        self._theme_preference = Qt.ColorScheme(saved)
        self._logger.info("Loaded theme preference: %s", self._theme_preference.name)

    def _save_settings(self):
        settings = QtCore.QSettings("Friture", "Friture")
        settings.setValue("themePreference", int(self._theme_preference.value))
        self._logger.info("Saved theme preference: %s", self._theme_preference.name)

    def _apply_theme_preference(self):
        """Apply the current theme preference to the application."""
        self._style_hints.setColorScheme(self._theme_preference)

    # Properties for QML access

    @pyqtProperty(int, notify=theme_changed)  # type: ignore
    def themePreference(self) -> int:
        """Current theme preference: 0=System, 1=Light, 2=Dark"""
        return int(self._theme_preference)

    @pyqtSlot(int)
    def setThemePreference(self, theme: int):
        """Set theme preference from QML (0=System, 1=Light, 2=Dark)."""
        new_preference = Qt.ColorScheme(theme)
        if new_preference != self._theme_preference:
            self._theme_preference = new_preference
            self._save_settings()
            self._apply_theme_preference()
            self.theme_changed.emit(int(new_preference.value))
            self._logger.info("Theme preference changed to: %s", new_preference.name)
