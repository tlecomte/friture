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

import os
import tempfile
import unittest

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from friture.settings import splash_enabled

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_app = QApplication.instance() or QApplication([])


class SplashSettingsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._settings_dir = tempfile.mkdtemp(prefix="friture-test-settings-")
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, cls._settings_dir)

    def setUp(self) -> None:
        QSettings("Friture", "Friture").clear()

    def test_splash_enabled_defaults_to_true(self) -> None:
        self.assertTrue(splash_enabled())

    def test_splash_disabled_when_setting_is_false(self) -> None:
        settings = QSettings("Friture", "Friture")
        settings.beginGroup("AudioBackend")
        settings.setValue("showSplash", False)
        settings.endGroup()
        settings.sync()

        self.assertFalse(splash_enabled())

    def test_splash_enabled_when_setting_is_true(self) -> None:
        settings = QSettings("Friture", "Friture")
        settings.beginGroup("AudioBackend")
        settings.setValue("showSplash", True)
        settings.endGroup()
        settings.sync()

        self.assertTrue(splash_enabled())
