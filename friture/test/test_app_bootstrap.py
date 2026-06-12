# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import logging
import os
import unittest
from unittest.mock import MagicMock

from PyQt5.QtWidgets import QApplication

from friture.analyzer import _linux_apply_dark_palette
from friture.test.helpers import IsolatedQSettings, ensure_qapplication


class AnalyzerBootstrapTest(unittest.TestCase):
    def test_dark_palette_applies_on_linux(self) -> None:
        ensure_qapplication()
        app = QApplication.instance()
        assert app is not None

        _linux_apply_dark_palette(app, logging.getLogger("test"))

        self.assertEqual(app.palette().color(app.palette().Window).name(), "#3d3d3e")

    def test_dark_palette_skipped_when_light_theme_forced(self) -> None:
        ensure_qapplication()
        app = QApplication.instance()
        assert app is not None
        original = app.palette().color(app.palette().Window)

        os.environ["FRITURE_LIGHT_THEME"] = "1"
        try:
            _linux_apply_dark_palette(app, logging.getLogger("test"))
        finally:
            del os.environ["FRITURE_LIGHT_THEME"]

        self.assertEqual(app.palette().color(app.palette().Window), original)


class SettingsDialogBootstrapTest(unittest.TestCase):
    def test_settings_dialog_opens_with_mocked_audio_backend(self) -> None:
        from unittest.mock import patch

        from PyQt5.QtWidgets import QWidget

        from friture.main_toolbar_view_model import MainToolbarViewModel
        from friture.settings import Settings_Dialog

        ensure_qapplication()
        parent = QWidget()
        toolbar = MainToolbarViewModel()

        backend = MagicMock()
        backend.get_readable_devices_list.return_value = ["Test Input"]
        backend.get_readable_current_channels.return_value = ["Ch 1"]
        backend.get_readable_current_device.return_value = 0

        with patch("friture.settings.get_audio_ingest", return_value=backend):
            dialog = Settings_Dialog(parent, toolbar)

        self.assertEqual(dialog.comboBox_inputDevice.count(), 1)
        self.assertTrue(dialog.checkbox_showSplash.isChecked())

    def test_saved_splash_setting_is_read_by_splash_enabled(self) -> None:
        from friture.settings import splash_enabled

        isolated = IsolatedQSettings()
        isolated.settings.beginGroup("AudioBackend")
        isolated.settings.setValue("showSplash", False)
        isolated.settings.endGroup()
        isolated.settings.sync()

        self.assertFalse(splash_enabled())
