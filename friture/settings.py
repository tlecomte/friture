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
from friture.global_calibration import GlobalCalibrationService
from friture.main_toolbar_view_model import MainToolbarViewModel
from friture.ui_settings import Ui_Settings_Dialog
from friture.calibration_settings_panel import CalibrationFormRows
from friture.level_meter import calibration_raw_rms_db

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
        global_calibration: GlobalCalibrationService | None = None,
        raw_rms_provider=None,
    ):
        QtWidgets.QDialog.__init__(self, parent)
        Ui_Settings_Dialog.__init__(self)

        self.logger = logging.getLogger(__name__)

        self._toolbar_view_model = toolbar_view_model
        self._catalog = catalog or get_input_device_catalog()
        self._global_calibration = global_calibration
        self._raw_rms_provider = raw_rms_provider
        self._settings_ref = None

        self.setupUi(self)

        self._setup_calibration_group()

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

    def _setup_calibration_group(self) -> None:
        if self._global_calibration is None:
            return

        self.calibrationGroup = QtWidgets.QGroupBox("Input calibration")
        calibration_layout = QtWidgets.QFormLayout(self.calibrationGroup)
        self._calibration_rows = CalibrationFormRows(
            calibration_layout, include_use_global=False
        )
        self._calibration_rows.button_calibrate.clicked.connect(
            self._calibrate_global_from_current
        )
        self._calibration_rows.doubleSpinBox_offset.valueChanged.connect(
            self._global_calibration.set_offset_db
        )
        self._calibration_rows.comboBox_unit.currentTextChanged.connect(
            self._global_calibration.set_unit_label
        )
        self._calibration_rows.lineEdit_reference.textChanged.connect(
            self._global_calibration.set_reference_note
        )
        self._global_calibration.changed.connect(self._sync_global_calibration_form)

        self.lineEdit_micCalFile = QtWidgets.QLineEdit()
        self.lineEdit_micCalFile.setReadOnly(True)
        self.lineEdit_micCalFile.setPlaceholderText("No microphone cal file loaded")
        mic_cal_buttons = QtWidgets.QHBoxLayout()
        self.button_micCalBrowse = QtWidgets.QPushButton("Browse…")
        self.button_micCalClear = QtWidgets.QPushButton("Clear")
        mic_cal_buttons.addWidget(self.button_micCalBrowse)
        mic_cal_buttons.addWidget(self.button_micCalClear)
        mic_cal_buttons.addStretch(1)
        calibration_layout.addRow("Mic cal file", self.lineEdit_micCalFile)
        calibration_layout.addRow("", mic_cal_buttons)
        self.label_micCalSummary = QtWidgets.QLabel("")
        self.label_micCalSummary.setWordWrap(True)
        calibration_layout.addRow("", self.label_micCalSummary)
        self.label_micCalStaleWarning = QtWidgets.QLabel(
            "⚠ Mic cal file not found — using cached data"
        )
        self.label_micCalStaleWarning.setWordWrap(True)
        self.label_micCalStaleWarning.setStyleSheet("color: orange;")
        self.label_micCalStaleWarning.setVisible(False)
        calibration_layout.addRow("", self.label_micCalStaleWarning)
        self.label_calibrationAge = QtWidgets.QLabel("")
        self.label_calibrationAge.setWordWrap(True)
        calibration_layout.addRow("", self.label_calibrationAge)
        self.button_micCalBrowse.clicked.connect(self._browse_mic_cal_file)
        self.button_micCalClear.clicked.connect(self._clear_mic_cal_file)

        startup_index = self.verticalLayout_5.indexOf(self.startupGroup)
        self.verticalLayout_5.insertWidget(startup_index, self.calibrationGroup)
        self._sync_global_calibration_form()
        self._sync_calibration_age()

    def _sync_global_calibration_form(self) -> None:
        if self._global_calibration is None:
            return
        cal = self._global_calibration.calibration
        self._calibration_rows.load(cal.offset_db, cal.unit_label, cal.reference_note)
        self._sync_mic_cal_form()
        self._sync_calibration_age()

    def _sync_calibration_age(self) -> None:
        if self._global_calibration is None or not hasattr(self, "label_calibrationAge"):
            return
        from datetime import datetime
        ts = getattr(self._global_calibration, "_calibrated_at", "")
        if not ts:
            self.label_calibrationAge.setText("Last calibrated: Unknown")
            return
        try:
            then = datetime.fromisoformat(ts)
            delta = datetime.now() - then
            days = delta.days
            if days == 0:
                text = "Last calibrated: today"
            elif days == 1:
                text = "Last calibrated: 1 day ago"
            else:
                text = f"Last calibrated: {days} days ago"
        except ValueError:
            text = "Last calibrated: Unknown"
        self.label_calibrationAge.setText(text)

    def _sync_mic_cal_form(self) -> None:
        if self._global_calibration is None:
            return
        import os
        path = self._global_calibration.mic_cal_file_path
        self.lineEdit_micCalFile.setText(path)
        mic_cal = self._global_calibration.mic_cal
        stale = bool(path and not os.path.exists(path))
        self.label_micCalStaleWarning.setVisible(stale)
        if mic_cal is None:
            if not stale:
                self.label_micCalSummary.setText(
                    "Load a factory .txt or REW .cal file to apply frequency correction globally."
                )
            return
        self.label_micCalSummary.setText(
            f"{mic_cal.summary()}. Frequency correction applies to spectrum widgets; "
            "use Calibrate… or offset for absolute SPL."
        )

    def _browse_mic_cal_file(self) -> None:
        if self._global_calibration is None:
            return
        path, _selected = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select microphone calibration file",
            self._global_calibration.mic_cal_file_path or "",
            "Calibration files (*.cal *.txt);;All files (*)",
        )
        if not path:
            return
        try:
            self._global_calibration.set_mic_cal_file(path)
        except Exception as exc:
            QtWidgets.QMessageBox.warning(
                self,
                "Calibration file",
                f"Could not load calibration file:\n{exc}",
            )
            return
        self._sync_global_calibration_form()

    def _clear_mic_cal_file(self) -> None:
        if self._global_calibration is None:
            return
        self._global_calibration.clear_mic_cal_file()
        self._sync_global_calibration_form()

    def _calibrate_global_from_current(self) -> None:
        if self._global_calibration is None or self._raw_rms_provider is None:
            return
        from friture.level_meter import calibrate_interactive
        calibrate_interactive(self._raw_rms_provider(), self._global_calibration, self)
        self._sync_global_calibration_form()

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

        if success and self._global_calibration is not None and self._settings_ref is not None:
            self._global_calibration.restoreState(
                self._settings_ref, device_key=self._current_device_key()
            )
            self._sync_global_calibration_form()

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

    def _current_device_key(self) -> str:
        if hasattr(self._catalog, "get_current_device_key"):
            return self._catalog.get_current_device_key()
        return ""

    def saveState(self, settings):
        if self._has_input_devices:
            settings.setValue("deviceName", self.comboBox_inputDevice.currentText())
            settings.setValue("firstChannel", self.comboBox_firstChannel.currentIndex())
            settings.setValue("secondChannel", self.comboBox_secondChannel.currentIndex())
            settings.setValue("duoInput", self.inputTypeButtonGroup.checkedId())
        settings.setValue("showPlayback", self.checkbox_showPlayback.checkState())
        settings.setValue("historyLength", self.spinBox_historyLength.value())
        settings.setValue("showSplash", self.checkbox_showSplash.isChecked())
        if self._global_calibration is not None:
            self._global_calibration.saveState(settings, device_key=self._current_device_key())

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
        self._settings_ref = settings
        if self._global_calibration is not None:
            self._global_calibration.restoreState(settings, device_key=self._current_device_key())
            self._sync_global_calibration_form()
