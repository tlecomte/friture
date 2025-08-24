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

import sys
import logging

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtProperty
from friture.audiobackend import AudioBackend
from friture.ui_settings import Ui_Settings_Dialog
import csv

no_input_device_title = "No audio input device found"

no_input_device_message = """No audio input device has been found.

Friture needs at least one input device. Please check your audio configuration.

Friture will now exit.
"""


class Settings_Dialog(QtWidgets.QDialog, Ui_Settings_Dialog):
    show_playback_changed = pyqtSignal(bool)
    history_length_changed = pyqtSignal(int)

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        Ui_Settings_Dialog.__init__(self)

        self.logger = logging.getLogger(__name__)

        # Setup the user interface
        self.setupUi(self)

        devices = AudioBackend().get_readable_devices_list()

        if devices == []:
            # no audio input device: display a message and exit
            QtWidgets.QMessageBox.critical(self, no_input_device_title, no_input_device_message)
            QtCore.QTimer.singleShot(0, self.exitOnInit)
            sys.exit(1)
            return

        for device in devices:
            self.comboBox_inputDevice.addItem(device)

        channels = AudioBackend().get_readable_current_channels()
        for channel in channels:
            self.comboBox_firstChannel.addItem(channel)
            self.comboBox_secondChannel.addItem(channel)

        current_device = AudioBackend().get_readable_current_device()
        self.comboBox_inputDevice.setCurrentIndex(current_device)

        first_channel = AudioBackend().get_current_first_channel()
        self.comboBox_firstChannel.setCurrentIndex(first_channel)
        second_channel = AudioBackend().get_current_second_channel()
        self.comboBox_secondChannel.setCurrentIndex(second_channel)

        # signals
        self.comboBox_inputDevice.currentIndexChanged.connect(self.input_device_changed)
        self.comboBox_firstChannel.activated.connect(self.first_channel_changed)
        self.comboBox_secondChannel.activated.connect(self.second_channel_changed)
        self.radioButton_single.toggled.connect(self.single_input_type_selected)
        self.radioButton_duo.toggled.connect(self.duo_input_type_selected)
        self.checkbox_showPlayback.stateChanged.connect(self.show_playback_checkbox_changed)
        self.spinBox_historyLength.editingFinished.connect(self.history_length_edit_finished)

        self.fileBox_compensation.clicked.connect(self.browse_compensation_file)
        self.clearButton.clicked.connect(self.compensation_file_cleared)

    @pyqtProperty(bool, notify=show_playback_changed) # type: ignore
    def show_playback(self) -> bool:
        return bool(self.checkbox_showPlayback.checkState())

    # slot
    # used when no audio input device has been found, to exit immediately
    def exitOnInit(self):
        QtWidgets.QApplication.instance().quit()

    # slot
    def input_device_changed(self, index):
        self.parent().ui.actionStart.setChecked(False)

        success, index = AudioBackend().select_input_device(index)

        self.comboBox_inputDevice.setCurrentIndex(index)

        if not success:
            # Note: the error message is a child of the settings dialog, so that
            # that dialog remains on top when the error message is closed
            error_message = QtWidgets.QErrorMessage(self)
            error_message.setWindowTitle("Input device error")
            error_message.showMessage("Impossible to use the selected input device, reverting to the previous one")

        # reset the channels
        channels = AudioBackend().get_readable_current_channels()

        self.comboBox_firstChannel.clear()
        self.comboBox_secondChannel.clear()

        for channel in channels:
            self.comboBox_firstChannel.addItem(channel)
            self.comboBox_secondChannel.addItem(channel)

        first_channel = AudioBackend().get_current_first_channel()
        self.comboBox_firstChannel.setCurrentIndex(first_channel)
        second_channel = AudioBackend().get_current_second_channel()
        self.comboBox_secondChannel.setCurrentIndex(second_channel)

        self.parent().ui.actionStart.setChecked(True)

    # slot
    def first_channel_changed(self, index):
        self.parent().ui.actionStart.setChecked(False)

        success, index = AudioBackend().select_first_channel(index)

        self.comboBox_firstChannel.setCurrentIndex(index)

        if not success:
            # Note: the error message is a child of the settings dialog, so that
            # that dialog remains on top when the error message is closed
            error_message = QtWidgets.QErrorMessage(self)
            error_message.setWindowTitle("Input device error")
            error_message.showMessage("Impossible to use the selected channel as the first channel, reverting to the previous one")

        self.parent().ui.actionStart.setChecked(True)

    # slot
    def second_channel_changed(self, index):
        self.parent().ui.actionStart.setChecked(False)

        success, index = AudioBackend().select_second_channel(index)

        self.comboBox_secondChannel.setCurrentIndex(index)

        if not success:
            # Note: the error message is a child of the settings dialog, so that
            # that dialog remains on top when the error message is closed
            error_message = QtWidgets.QErrorMessage(self)
            error_message.setWindowTitle("Input device error")
            error_message.showMessage("Impossible to use the selected channel as the second channel, reverting to the previous one")

        self.parent().ui.actionStart.setChecked(True)

    # slot
    def single_input_type_selected(self, checked):
        if checked:
            self.groupBox_second.setEnabled(False)
            AudioBackend().set_single_input()
            self.logger.info("Switching to single input")

    # slot
    def duo_input_type_selected(self, checked):
        if checked:
            self.groupBox_second.setEnabled(True)
            AudioBackend().set_duo_input()
            self.logger.info("Switching to difference between two inputs")

    # slot
    def show_playback_checkbox_changed(self, state: int) -> None:
        self.show_playback_changed.emit(bool(state))

    # slot
    def history_length_edit_finished(self) -> None:
        self.history_length_changed.emit(self.spinBox_historyLength.value())
    
    def browse_compensation_file(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, "Open compensation file", "", "Compensation files (*.*)")[0]
        self.fileBox_compensation.setText(file_name)
        self.load_compensation_file()
    
    def load_compensation_file(self):
        file_name = self.fileBox_compensation.text()
        if file_name:
            try:
                with open(file_name, newline='') as csvfile:
                    csvreader = csv.reader(csvfile)
                    self.parent().original_calibration = []
                    self.parent().original_calibration_freqs = []
                    for row in csvreader:
                        if row[0][0].isdigit():
                            dict = row[0].split()
                            self.parent().original_calibration.append(float(dict[1]))
                            self.parent().original_calibration_freqs.append(float(dict[0]))
                    
            except Exception as e:
                self.logger.error(f"Failed to load compensation file: {e}")
        else:
            self.parent().original_calibration = [0, 0]
            self.parent().original_calibration_freqs = [0, 20000]
        
        self.parent().recalculate_calibration()
    
    def compensation_file_cleared(self):
        self.fileBox_compensation.setText("")
        self.load_compensation_file()

    # method
    def saveState(self, settings):
        # for the input device, we search by name instead of index, since
        # we do not know if the device order stays the same between sessions
        settings.setValue("deviceName", self.comboBox_inputDevice.currentText())
        settings.setValue("firstChannel", self.comboBox_firstChannel.currentIndex())
        settings.setValue("secondChannel", self.comboBox_secondChannel.currentIndex())
        settings.setValue("duoInput", self.inputTypeButtonGroup.checkedId())
        settings.setValue("showPlayback", self.checkbox_showPlayback.checkState())
        settings.setValue("historyLength", self.spinBox_historyLength.value())
        settings.setValue("compensationFile", self.fileBox_compensation.text())

    # method
    def restoreState(self, settings):
        device_name = settings.value("deviceName", "")
        device_index = self.comboBox_inputDevice.findText(device_name)
        # change the device only if it exists in the device list
        if device_index >= 0:
            compensation_file = settings.value("compensationFile", "")
            self.fileBox_compensation.setText(compensation_file)
            self.load_compensation_file()
            self.comboBox_inputDevice.setCurrentIndex(device_index)
            channel = settings.value("firstChannel", 0, type=int)
            self.comboBox_firstChannel.setCurrentIndex(channel)
            channel = settings.value("secondChannel", 0, type=int)
            self.comboBox_secondChannel.setCurrentIndex(channel)
            duo_input_id = settings.value("duoInput", 0, type=int)
            self.inputTypeButtonGroup.button(duo_input_id).setChecked(True)
        self.checkbox_showPlayback.setCheckState(settings.value("showPlayback", 0, type=int))
        self.spinBox_historyLength.setValue(settings.value("historyLength", 30, type=int))
        # need to emit this because setValue doesn't emit editFinished
        self.history_length_changed.emit(self.spinBox_historyLength.value())
