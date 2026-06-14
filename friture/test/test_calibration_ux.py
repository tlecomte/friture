# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Tests for calibration UX: stale mic cal warning and calibration age display."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from friture.test.helpers import IsolatedQSettings, ensure_qapplication, make_parent_widget


class CalibrationAgeDisplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ensure_qapplication()

    def _make_dialog(self):
        from friture.main_toolbar_view_model import MainToolbarViewModel
        from friture.settings import Settings_Dialog
        from friture.global_calibration import GlobalCalibrationService
        from PyQt5.QtWidgets import QWidget

        catalog = MagicMock()
        catalog.get_readable_devices_list.return_value = ["Test Mic"]
        catalog.get_readable_current_channels.return_value = ["0"]
        catalog.get_readable_current_device.return_value = 0
        catalog.get_current_first_channel.return_value = 0
        catalog.get_current_second_channel.return_value = 0
        catalog.select_input_device.return_value = (True, 0)
        catalog.get_current_device_key.return_value = ""

        self._parent = QWidget()
        cal = GlobalCalibrationService(self._parent)
        dialog = Settings_Dialog(
            self._parent, MainToolbarViewModel(),
            catalog=catalog, global_calibration=cal,
        )
        self._dialog = dialog
        return dialog, cal

    def test_age_label_shows_today_after_recent_calibration(self) -> None:
        from datetime import datetime
        dialog, cal = self._make_dialog()
        cal._calibrated_at = datetime.now().isoformat()

        dialog._sync_calibration_age()

        text = dialog.label_calibrationAge.text()
        self.assertIn("today", text.lower())

    def test_age_label_shows_unknown_when_no_timestamp(self) -> None:
        dialog, cal = self._make_dialog()
        dialog._sync_calibration_age()

        self.assertIn("unknown", dialog.label_calibrationAge.text().lower())

    def test_age_label_shows_unknown_on_malformed_timestamp(self) -> None:
        dialog, cal = self._make_dialog()
        cal._calibrated_at = "not-a-date"

        dialog._sync_calibration_age()

        self.assertIn("unknown", dialog.label_calibrationAge.text().lower())

    def test_age_label_shows_days_ago_for_old_calibration(self) -> None:
        from datetime import datetime, timedelta
        dialog, cal = self._make_dialog()
        cal._calibrated_at = (datetime.now() - timedelta(days=5)).isoformat()

        dialog._sync_calibration_age()

        self.assertIn("5", dialog.label_calibrationAge.text())
        self.assertIn("day", dialog.label_calibrationAge.text())


class StaleMicCalWarningTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ensure_qapplication()

    def _make_dialog_with_cal(self):
        from friture.main_toolbar_view_model import MainToolbarViewModel
        from friture.settings import Settings_Dialog
        from friture.global_calibration import GlobalCalibrationService
        from PyQt5.QtWidgets import QWidget

        catalog = MagicMock()
        catalog.get_readable_devices_list.return_value = ["Test Mic"]
        catalog.get_readable_current_channels.return_value = ["0"]
        catalog.get_readable_current_device.return_value = 0
        catalog.get_current_first_channel.return_value = 0
        catalog.get_current_second_channel.return_value = 0
        catalog.select_input_device.return_value = (True, 0)
        catalog.get_current_device_key.return_value = ""

        self._parent = QWidget()
        cal = GlobalCalibrationService(self._parent)
        dialog = Settings_Dialog(
            self._parent, MainToolbarViewModel(),
            catalog=catalog, global_calibration=cal
        )
        self._dialog = dialog
        return dialog, cal

    def test_no_warning_when_no_mic_cal_path(self) -> None:
        dialog, cal = self._make_dialog_with_cal()

        cal.mic_cal_file_path = ""
        cal.mic_cal = None
        dialog._sync_mic_cal_form()

        if hasattr(dialog, "label_micCalStaleWarning"):
            self.assertTrue(dialog.label_micCalStaleWarning.isHidden())

    def test_warning_shown_when_path_set_but_file_missing(self) -> None:
        dialog, cal = self._make_dialog_with_cal()

        cal.mic_cal_file_path = "/nonexistent/path/mic.cal"
        cal.mic_cal = None

        with patch("os.path.exists", return_value=False):
            dialog._sync_mic_cal_form()

        self.assertFalse(dialog.label_micCalStaleWarning.isHidden())
        self.assertIn("not found", dialog.label_micCalStaleWarning.text().lower())

    def test_warning_hidden_when_file_exists_and_loaded(self) -> None:
        dialog, cal = self._make_dialog_with_cal()

        with tempfile.NamedTemporaryFile(suffix=".cal", delete=False) as f:
            cal.mic_cal_file_path = f.name

        fake_mic_cal = MagicMock()
        fake_mic_cal.summary.return_value = "Test mic cal"
        cal.mic_cal = fake_mic_cal

        try:
            with patch("os.path.exists", return_value=True):
                dialog._sync_mic_cal_form()

            self.assertTrue(dialog.label_micCalStaleWarning.isHidden())
        finally:
            os.unlink(cal.mic_cal_file_path)

    def test_no_warning_when_file_exists_but_parse_failed(self) -> None:
        """File exists on disk but cal is None (parse failed, no cache) — stale=False, no warning."""
        dialog, cal = self._make_dialog_with_cal()

        cal.mic_cal_file_path = "/some/path/mic.cal"
        cal.mic_cal = None

        with patch("os.path.exists", return_value=True):
            dialog._sync_mic_cal_form()

        self.assertTrue(dialog.label_micCalStaleWarning.isHidden())
