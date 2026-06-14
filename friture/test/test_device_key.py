# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Tests for per-device calibration key generation and QSettings scoping."""

import unittest

from friture.test.helpers import IsolatedQSettings, ensure_qapplication, make_parent_widget


class ComputeDeviceKeyTest(unittest.TestCase):
    def test_composite_key_from_device_dict(self) -> None:
        from unittest.mock import patch
        from friture.input_device_catalog import compute_device_key

        mock_hostapi = {"name": "ALSA"}
        device = {"name": "Focusrite USB Audio", "hostapi": 0}

        with patch("sounddevice.query_hostapis", return_value=mock_hostapi):
            key = compute_device_key(device)

        self.assertEqual(key, "Focusrite_USB_Audio__ALSA")

    def test_portaudio_error_returns_empty_string(self) -> None:
        from unittest.mock import patch
        import sounddevice
        from friture.input_device_catalog import compute_device_key

        device = {"name": "Broken Mic", "hostapi": 0}

        with patch("sounddevice.query_hostapis", side_effect=sounddevice.PortAudioError("fail")):
            key = compute_device_key(device)

        self.assertEqual(key, "")


class PerDeviceCalibrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ensure_qapplication()

    def setUp(self) -> None:
        self.parent = make_parent_widget()
        self.isolated = IsolatedQSettings()

    def test_savestate_writes_offset_under_device_profile(self) -> None:
        from friture.global_calibration import GlobalCalibrationService

        service = GlobalCalibrationService(self.parent)
        service.set_offset_db(12.5)
        service.saveState(self.isolated.settings, device_key="focusrite__alsa")

        self.isolated.settings.beginGroup("GlobalCalibration/profiles/focusrite__alsa")
        stored = self.isolated.settings.value("offsetDb", type=float)
        self.isolated.settings.endGroup()

        self.assertAlmostEqual(stored, 12.5)

    def test_savestate_no_device_key_writes_flat_key(self) -> None:
        from friture.global_calibration import GlobalCalibrationService

        service = GlobalCalibrationService(self.parent)
        service.set_offset_db(6.0)
        service.saveState(self.isolated.settings, device_key="")

        stored = self.isolated.settings.value("offsetDb", type=float)
        self.assertAlmostEqual(stored, 6.0)

    def test_restorestate_reads_from_device_profile(self) -> None:
        from friture.global_calibration import GlobalCalibrationService

        self.isolated.settings.beginGroup("GlobalCalibration/profiles/focusrite__alsa")
        self.isolated.settings.setValue("offsetDb", 9.0)
        self.isolated.settings.endGroup()

        service = GlobalCalibrationService(self.parent)
        service.restoreState(self.isolated.settings, device_key="focusrite__alsa")

        self.assertAlmostEqual(service.calibration.offset_db, 9.0)

    def test_restorestate_falls_back_to_flat_key_for_unknown_device(self) -> None:
        from friture.global_calibration import GlobalCalibrationService

        self.isolated.settings.setValue("offsetDb", 3.0)
        service = GlobalCalibrationService(self.parent)
        service.restoreState(self.isolated.settings, device_key="unknown__device")

        self.assertAlmostEqual(service.calibration.offset_db, 3.0)

    def test_old_flat_keys_not_deleted_on_device_save(self) -> None:
        from friture.global_calibration import GlobalCalibrationService

        self.isolated.settings.setValue("offsetDb", 5.0)
        service = GlobalCalibrationService(self.parent)
        service.set_offset_db(5.0)
        service.saveState(self.isolated.settings, device_key="focusrite__alsa")

        self.assertTrue(self.isolated.settings.contains("offsetDb"))


class SettingsDialogDeviceKeyTest(unittest.TestCase):
    """Settings_Dialog must thread live device key into GlobalCalibrationService."""

    @classmethod
    def setUpClass(cls) -> None:
        ensure_qapplication()

    def _make_dialog(self, device_key="focusrite__alsa"):
        from unittest.mock import MagicMock
        from friture.main_toolbar_view_model import MainToolbarViewModel
        from friture.settings import Settings_Dialog
        from friture.global_calibration import GlobalCalibrationService
        from PyQt5.QtWidgets import QWidget

        catalog = MagicMock()
        catalog.get_readable_devices_list.return_value = ["Focusrite USB Audio"]
        catalog.get_readable_current_channels.return_value = ["L", "R"]
        catalog.get_readable_current_device.return_value = 0
        catalog.get_current_first_channel.return_value = 0
        catalog.get_current_second_channel.return_value = 0
        catalog.select_input_device.return_value = (True, 0)
        catalog.get_current_device_key.return_value = device_key

        self._parent = QWidget()  # keep alive for test duration
        cal = GlobalCalibrationService(self._parent)
        dialog = Settings_Dialog(self._parent, MainToolbarViewModel(), catalog=catalog, global_calibration=cal)
        self._dialog = dialog  # keep alive
        return dialog, cal, catalog

    def test_savestate_passes_device_key_to_calibration_service(self) -> None:
        from unittest.mock import patch, MagicMock
        dialog, cal, catalog = self._make_dialog("focusrite__alsa")
        iso = IsolatedQSettings()

        dialog.saveState(iso.settings)

        iso.settings.beginGroup("GlobalCalibration/profiles/focusrite__alsa")
        exists = iso.settings.contains("offsetDb")
        iso.settings.endGroup()
        self.assertTrue(exists)

    def test_restorestate_passes_device_key_to_calibration_service(self) -> None:
        dialog, cal, catalog = self._make_dialog("focusrite__alsa")
        iso = IsolatedQSettings()

        iso.settings.beginGroup("GlobalCalibration/profiles/focusrite__alsa")
        iso.settings.setValue("offsetDb", 7.5)
        iso.settings.endGroup()

        dialog.restoreState(iso.settings)

        self.assertAlmostEqual(cal.calibration.offset_db, 7.5)

    def test_device_switch_loads_new_device_calibration(self) -> None:
        """E3: input_device_changed() restores calibration for the newly selected device."""
        dialog, cal, catalog = self._make_dialog("focusrite__alsa")
        iso = IsolatedQSettings()

        # Pre-seed calibration for a second device
        iso.settings.beginGroup("GlobalCalibration/profiles/behringer__alsa")
        iso.settings.setValue("offsetDb", 14.0)
        iso.settings.endGroup()
        dialog.saveState(iso.settings)

        # Simulate switch: old key returned first (before select), new key after
        catalog.get_current_device_key.side_effect = ["focusrite__alsa", "behringer__alsa"]
        catalog.select_input_device.return_value = (True, 1)
        dialog._settings_ref = iso.settings
        dialog.input_device_changed(1)

        self.assertAlmostEqual(cal.calibration.offset_db, 14.0)


class SanitizeDeviceKeyTest(unittest.TestCase):
    def test_simple_name_and_api_joined_by_double_underscore(self) -> None:
        from friture.input_device_catalog import sanitize_device_key

        key = sanitize_device_key("Focusrite USB Audio", "ALSA")

        self.assertEqual(key, "Focusrite_USB_Audio__ALSA")

    def test_slashes_in_name_replaced_with_underscore(self) -> None:
        from friture.input_device_catalog import sanitize_device_key

        key = sanitize_device_key("USB Audio/MIDI Interface", "ALSA")

        self.assertNotIn("/", key)
        self.assertIn("__ALSA", key)

    def test_empty_name_produces_unknown_prefix(self) -> None:
        from friture.input_device_catalog import sanitize_device_key

        key = sanitize_device_key("", "ALSA")

        self.assertEqual(key, "__unknown____ALSA")

    def test_empty_api_produces_empty_suffix(self) -> None:
        from friture.input_device_catalog import sanitize_device_key

        key = sanitize_device_key("My Mic", "")

        self.assertEqual(key, "My_Mic__")

    def test_key_safe_for_qsettings_group(self) -> None:
        from friture.input_device_catalog import sanitize_device_key

        key = sanitize_device_key("Focusrite Scarlett 2i2 (3rd Gen.)", "ALSA")

        self.assertNotIn("/", key)
        self.assertNotIn("\\", key)
        self.assertTrue(len(key) > 0)
