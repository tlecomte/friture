# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

import sys
import unittest
from unittest.mock import MagicMock, patch

from friture.test.helpers import ensure_qapplication


def make_catalog(
    devices: list[str] | None = None,
    channels: list[str] | None = None,
) -> MagicMock:
    device_list = ["Test Input (1 ch)"] if devices is None else devices
    channel_list = ["0"] if channels is None else channels
    catalog = MagicMock()
    catalog.get_readable_devices_list.return_value = device_list
    catalog.get_readable_current_channels.return_value = channel_list
    catalog.get_readable_current_device.return_value = 0
    catalog.get_current_first_channel.return_value = 0
    catalog.get_current_second_channel.return_value = 0
    catalog.select_input_device.return_value = (True, 0)
    catalog.select_first_channel.return_value = (True, 0)
    catalog.select_second_channel.return_value = (True, 0)
    return catalog


class SettingsDialogCatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ensure_qapplication()

    def test_settings_dialog_uses_injected_catalog_without_patch(self) -> None:
        from PyQt5.QtWidgets import QWidget

        from friture.main_toolbar_view_model import MainToolbarViewModel
        from friture.settings import Settings_Dialog

        parent = QWidget()
        dialog = Settings_Dialog(
            parent,
            MainToolbarViewModel(),
            catalog=make_catalog(["Mic A", "Mic B"]),
        )

        self.assertTrue(dialog.has_input_devices())
        self.assertEqual(dialog.comboBox_inputDevice.count(), 2)

    def test_empty_catalog_does_not_call_sys_exit(self) -> None:
        from PyQt5.QtWidgets import QWidget

        from friture.main_toolbar_view_model import MainToolbarViewModel
        from friture.settings import Settings_Dialog

        parent = QWidget()
        with patch.object(sys, "exit") as mock_exit:
            dialog = Settings_Dialog(
                parent,
                MainToolbarViewModel(),
                catalog=make_catalog([]),
            )

        mock_exit.assert_not_called()
        self.assertFalse(dialog.has_input_devices())
        self.assertEqual(dialog.comboBox_inputDevice.count(), 0)


class ApplySavedInputSelectionTest(unittest.TestCase):
    def test_selects_saved_device_and_channels(self) -> None:
        from friture.input_device_catalog import apply_saved_input_selection

        catalog = make_catalog(["Mic A", "Mic B"])
        catalog.select_input_device.return_value = (True, 1)

        self.assertTrue(
            apply_saved_input_selection(catalog, "Mic B", 0, 1, duo_input=False)
        )

        catalog.select_input_device.assert_called_once_with(1)
        catalog.select_first_channel.assert_called_once_with(0)
        catalog.select_second_channel.assert_called_once_with(1)
        catalog.set_single_input.assert_called_once_with()
        catalog.set_duo_input.assert_not_called()

    def test_duo_input_mode(self) -> None:
        from friture.input_device_catalog import apply_saved_input_selection

        catalog = make_catalog(["Mic A"])
        catalog.select_input_device.return_value = (True, 0)

        apply_saved_input_selection(catalog, "Mic A", 0, 1, duo_input=True)

        catalog.set_duo_input.assert_called_once_with()
        catalog.set_single_input.assert_not_called()

    def test_unknown_device_returns_false(self) -> None:
        from friture.input_device_catalog import apply_saved_input_selection

        catalog = make_catalog(["Mic A"])

        self.assertFalse(
            apply_saved_input_selection(catalog, "Missing Mic", 0, 0, duo_input=False)
        )
        catalog.select_input_device.assert_not_called()


class SettingsRestoreStateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ensure_qapplication()

    def test_restore_state_applies_saved_device_to_catalog(self) -> None:
        from PyQt5.QtCore import QSettings
        from PyQt5.QtWidgets import QWidget

        from friture.main_toolbar_view_model import MainToolbarViewModel
        from friture.settings import Settings_Dialog

        catalog = make_catalog(["Mic A", "Mic B"], ["0", "1"])
        catalog.select_input_device.return_value = (True, 1)
        catalog.get_current_first_channel.return_value = 0
        catalog.get_current_second_channel.return_value = 1

        parent = QWidget()
        dialog = Settings_Dialog(
            parent,
            MainToolbarViewModel(),
            catalog=catalog,
        )
        single_input_id = dialog.inputTypeButtonGroup.id(dialog.radioButton_single)

        settings = QSettings()
        settings.setValue("deviceName", "Mic B")
        settings.setValue("firstChannel", 0)
        settings.setValue("secondChannel", 1)
        settings.setValue("duoInput", single_input_id)

        dialog.restoreState(settings)

        catalog.select_input_device.assert_called_with(1)
        catalog.set_single_input.assert_called()


class RequireInputDevicesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ensure_qapplication()

    def test_require_input_devices_exits_when_catalog_empty(self) -> None:
        from friture.input_device_catalog import require_input_devices

        catalog = make_catalog([])

        with patch.object(sys, "exit") as mock_exit, patch(
            "friture.input_device_catalog.QtWidgets.QMessageBox.critical"
        ), patch("friture.input_device_catalog.QtCore.QTimer.singleShot"):
            require_input_devices(None, catalog)

        mock_exit.assert_called_once_with(1)

    def test_require_input_devices_noop_when_devices_present(self) -> None:
        from friture.input_device_catalog import require_input_devices

        with patch.object(sys, "exit") as mock_exit:
            require_input_devices(None, make_catalog(["Mic"]))

        mock_exit.assert_not_called()
