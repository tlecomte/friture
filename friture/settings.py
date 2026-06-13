#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

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

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtProperty

from friture.input_device_catalog import (
    InputDeviceCatalog,
    apply_saved_input_selection,
    get_input_device_catalog,
)
from friture.main_toolbar_view_model import MainToolbarViewModel
from friture.ui_settings import Ui_Settings_Dialog

# Backward-compatible re-exports for callers/tests.
no_input_device_title = "No audio input device found"
no_input_device_message = """No audio input device has been found.

Friture needs at least one input device. Please check your audio configuration.

Friture will now exit.
"""


def splash_enabled() -> bool:
    settings = QtCore.QSettings("Friture", "Friture")
    settings.beginGroup("AudioBackend")
    enabled = settings.value("showSplash", True, type=bool)
    settings.endGroup()
    return enabled


class Settings_Dialog(QtWidgets.QDialog, Ui_Settings_Dialog):
    show_playback_changed = pyqtSignal(bool)
    history_length_changed = pyqtSignal(int)

    def __init__(
        self,
        parent,
        toolbar_view_model: MainToolbarViewModel,
        catalog: InputDeviceCatalog | None = None,
    ):
        QtWidgets.QDialog.__init__(self, parent)
        Ui_Settings_Dialog.__init__(self)

        self.logger = logging.getLogger(__name__)

        self._toolbar_view_model = toolbar_view_model
        self._catalog = catalog or get_input_device_catalog()

        self.setupUi(self)

        devices = self._catalog.get_readable_devices_list()
        self._has_input_devices = len(devices) > 0

        if self._has_input_devices:
            self._populate_input_devices(devices)
        else:
            self.inputGroup.setEnabled(False)
            self.groupBox_second.setEnabled(False)

        self.checkbox_showPlayback.stateChanged.connect(self.show_playback_checkbox_changed)
        self.spinBox_historyLength.editingFinished.connect(self.history_length_edit_finished)
        self.buttonBox.rejected.connect(self.close)

    def has_input_devices(self) -> bool:
        return self._has_input_devices

    def _populate_input_devices(self, devices: list[str]) -> None:
        for device in devices:
            self.comboBox_inputDevice.addItem(device)

        channels = self._catalog.get_readable_current_channels()
        for channel in channels:
            self.comboBox_firstChannel.addItem(channel)
            self.comboBox_secondChannel.addItem(channel)

        current_device = self._catalog.get_readable_current_device()
        self.comboBox_inputDevice.setCurrentIndex(current_device)

        first_channel = self._catalog.get_current_first_channel()
        self.comboBox_firstChannel.setCurrentIndex(first_channel)
        second_channel = self._catalog.get_current_second_channel()
        self.comboBox_secondChannel.setCurrentIndex(second_channel)

        self.comboBox_inputDevice.currentIndexChanged.connect(self.input_device_changed)
        self.comboBox_firstChannel.activated.connect(self.first_channel_changed)
        self.comboBox_secondChannel.activated.connect(self.second_channel_changed)
        self.radioButton_single.toggled.connect(self.single_input_type_selected)
        self.radioButton_duo.toggled.connect(self.duo_input_type_selected)

    @pyqtProperty(bool, notify=show_playback_changed)  # type: ignore
    def show_playback(self) -> bool:
        return bool(self.checkbox_showPlayback.checkState())

    def input_device_changed(self, index):
        self._toolbar_view_model.recording = False

        success, index = self._catalog.select_input_device(index)

        self.comboBox_inputDevice.setCurrentIndex(index)

        if not success:
            error_message = QtWidgets.QErrorMessage(self)
            error_message.setWindowTitle("Input device error")
            error_message.showMessage(
                "Impossible to use the selected input device, reverting to the previous one"
            )

        self._sync_channel_combos()

        self._toolbar_view_model.recording = True

    def _sync_channel_combos(self) -> None:
        channels = self._catalog.get_readable_current_channels()

        self.comboBox_firstChannel.clear()
        self.comboBox_secondChannel.clear()

        for channel in channels:
            self.comboBox_firstChannel.addItem(channel)
            self.comboBox_secondChannel.addItem(channel)

        self.comboBox_firstChannel.setCurrentIndex(
            self._catalog.get_current_first_channel()
        )
        self.comboBox_secondChannel.setCurrentIndex(
            self._catalog.get_current_second_channel()
        )

    def first_channel_changed(self, index):
        self._toolbar_view_model.recording = False

        success, index = self._catalog.select_first_channel(index)

        self.comboBox_firstChannel.setCurrentIndex(index)

        if not success:
            error_message = QtWidgets.QErrorMessage(self)
            error_message.setWindowTitle("Input device error")
            error_message.showMessage(
                "Impossible to use the selected channel as the first channel, reverting to the previous one"
            )

        self._toolbar_view_model.recording = True

    def second_channel_changed(self, index):
        self._toolbar_view_model.recording = False

        success, index = self._catalog.select_second_channel(index)

        self.comboBox_secondChannel.setCurrentIndex(index)

        if not success:
            error_message = QtWidgets.QErrorMessage(self)
            error_message.setWindowTitle("Input device error")
            error_message.showMessage(
                "Impossible to use the selected channel as the second channel, reverting to the previous one"
            )

        self._toolbar_view_model.recording = True

    def single_input_type_selected(self, checked):
        if checked:
            self.groupBox_second.setEnabled(False)
            self._catalog.set_single_input()
            self.logger.info("Switching to single input")

    def duo_input_type_selected(self, checked):
        if checked:
            self.groupBox_second.setEnabled(True)
            self._catalog.set_duo_input()
            self.logger.info("Switching to difference between two inputs")

    def show_playback_checkbox_changed(self, state: int) -> None:
        self.show_playback_changed.emit(bool(state))

    def history_length_edit_finished(self) -> None:
        self.history_length_changed.emit(self.spinBox_historyLength.value())

    def saveState(self, settings):
        if self._has_input_devices:
            settings.setValue("deviceName", self.comboBox_inputDevice.currentText())
            settings.setValue("firstChannel", self.comboBox_firstChannel.currentIndex())
            settings.setValue("secondChannel", self.comboBox_secondChannel.currentIndex())
            settings.setValue("duoInput", self.inputTypeButtonGroup.checkedId())
        settings.setValue("showPlayback", self.checkbox_showPlayback.checkState())
        settings.setValue("historyLength", self.spinBox_historyLength.value())
        settings.setValue("showSplash", self.checkbox_showSplash.isChecked())

    def restoreState(self, settings):
        if self._has_input_devices:
            device_name = settings.value("deviceName", "")
            first_channel = settings.value("firstChannel", 0, type=int)
            second_channel = settings.value("secondChannel", 0, type=int)
            duo_input_id = settings.value("duoInput", 0, type=int)
            duo_input = duo_input_id == self.inputTypeButtonGroup.id(
                self.radioButton_duo
            )

            if apply_saved_input_selection(
                self._catalog,
                device_name,
                first_channel,
                second_channel,
                duo_input,
            ):
                device_index = self.comboBox_inputDevice.findText(device_name)
                self.comboBox_inputDevice.setCurrentIndex(device_index)
                self._sync_channel_combos()
                self.comboBox_firstChannel.setCurrentIndex(
                    self._catalog.get_current_first_channel()
                )
                self.comboBox_secondChannel.setCurrentIndex(
                    self._catalog.get_current_second_channel()
                )
                button = self.inputTypeButtonGroup.button(duo_input_id)
                if button is not None:
                    button.setChecked(True)
                self.groupBox_second.setEnabled(duo_input)
        self.checkbox_showPlayback.setCheckState(settings.value("showPlayback", 0, type=int))
        self.spinBox_historyLength.setValue(settings.value("historyLength", 30, type=int))
        self.checkbox_showSplash.setChecked(settings.value("showSplash", True, type=bool))
        self.history_length_changed.emit(self.spinBox_historyLength.value())
