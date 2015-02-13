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

from PyQt4 import QtGui, QtCore
from friture.ui_settings import Ui_Settings_Dialog

no_input_device_title = "No audio input device found"

no_input_device_message = """No audio input device has been found.

Please check your audio configuration.

Friture will now exit.
"""

class Settings_Dialog(QtGui.QDialog, Ui_Settings_Dialog):
	def __init__(self, parent, logger, audiobackend):
		QtGui.QDialog.__init__(self, parent)
		Ui_Settings_Dialog.__init__(self)
		
		# Setup the user interface
		self.setupUi(self)

		self.audiobackend = audiobackend
		self.logger = logger

		devices = self.audiobackend.get_readable_devices_list()

		if devices == []:
			# no audio input device: display a message and exit
			QtGui.QMessageBox.critical(self, no_input_device_title, no_input_device_message)
			QtCore.QTimer.singleShot(0, self.exitOnInit)
			return

		for device in devices:
			self.comboBox_inputDevice.addItem(device)

		channels = self.audiobackend.get_readable_current_channels()
		for channel in channels:
			self.comboBox_firstChannel.addItem(channel)
			self.comboBox_secondChannel.addItem(channel)

		current_device = self.audiobackend.get_readable_current_device()
		self.comboBox_inputDevice.setCurrentIndex(current_device)

		first_channel = self.audiobackend.get_current_first_channel()
		self.comboBox_firstChannel.setCurrentIndex(first_channel)
		second_channel = self.audiobackend.get_current_second_channel()
		self.comboBox_secondChannel.setCurrentIndex(second_channel)

		# signals
		self.comboBox_inputDevice.currentIndexChanged.connect(self.input_device_changed)
		self.comboBox_firstChannel.currentIndexChanged.connect(self.first_channel_changed)
		self.comboBox_secondChannel.currentIndexChanged.connect(self.second_channel_changed)
		self.radioButton_single.toggled.connect(self.single_input_type_selected)
		self.radioButton_duo.toggled.connect(self.duo_input_type_selected)

	# slot
	# used when no audio input device has been found, to exit immediately
	def exitOnInit(self):
		QtGui.QApplication.instance().quit()

	# slot
	def input_device_changed(self, index):
		self.parent().ui.actionStart.setChecked(False)
		
		success, index = self.audiobackend.select_input_device(index)
		
		self.comboBox_inputDevice.setCurrentIndex(index)
		
		if not success:
			# Note: the error message is a child of the settings dialog, so that
			# that dialog remains on top when the error message is closed
			error_message = QErrorMessage(self)
			error_message.setWindowTitle("Input device error")
			error_message.showMessage("Impossible to use the selected input device, reverting to the previous one")
		
		# reset the channels
		first_channel = self.audiobackend.get_current_first_channel()
		self.comboBox_firstChannel.setCurrentIndex(first_channel)
		second_channel = self.audiobackend.get_current_second_channel()
		self.comboBox_secondChannel.setCurrentIndex(second_channel)

		self.parent().ui.actionStart.setChecked(True)

	# slot
	def first_channel_changed(self, index):
		self.parent().ui.actionStart.setChecked(False)
		
		success, index = self.audiobackend.select_first_channel(index)
		
		self.comboBox_firstChannel.setCurrentIndex(index)
		
		if not success:
			# Note: the error message is a child of the settings dialog, so that
			# that dialog remains on top when the error message is closed
			error_message = QErrorMessage(self)
			error_message.setWindowTitle("Input device error")
			error_message.showMessage("Impossible to use the selected channel as the first channel, reverting to the previous one")
		
		self.parent().ui.actionStart.setChecked(True)

	# slot
	def second_channel_changed(self, index):
		self.parent().ui.actionStart.setChecked(False)
		
		success, index = self.audiobackend.select_second_channel(index)
		
		self.comboBox_secondChannel.setCurrentIndex(index)
		
		if not success:
			# Note: the error message is a child of the settings dialog, so that
			# that dialog remains on top when the error message is closed
			error_message = QErrorMessage(self)
			error_message.setWindowTitle("Input device error")
			error_message.showMessage("Impossible to use the selected channel as the second channel, reverting to the previous one")
		
		self.parent().ui.actionStart.setChecked(True)

	# slot
	def single_input_type_selected(self, checked):
		if checked:
			self.groupBox_second.setEnabled(False)
			self.audiobackend.set_single_input()
			self.logger.push("Switching to single input")

	# slot
	def duo_input_type_selected(self, checked):
		if checked:
			self.groupBox_second.setEnabled(True)
			self.audiobackend.set_duo_input()
			self.logger.push("Switching to difference between two inputs")

	# method
	def saveState(self, settings):
		# for the input device, we search by name instead of index, since
		# we do not know if the device order stays the same between sessions
		settings.setValue("deviceName", self.comboBox_inputDevice.currentText())
		settings.setValue("firstChannel", self.comboBox_firstChannel.currentIndex())
		settings.setValue("secondChannel", self.comboBox_secondChannel.currentIndex())
		settings.setValue("duoInput", self.inputTypeButtonGroup.checkedId())

	# method
	def restoreState(self, settings):
		device_name = settings.value("deviceName", "").toString()
		id = self.comboBox_inputDevice.findText(device_name)
		# change the device only if it exists in the device list
		if id >= 0:
			self.comboBox_inputDevice.setCurrentIndex(id)
			(channel, ok) = settings.value("firstChannel", 0).toInt()
			self.comboBox_firstChannel.setCurrentIndex(channel)
			(channel, ok) = settings.value("secondChannel", 0).toInt()
			self.comboBox_secondChannel.setCurrentIndex(channel)
			(duo_input_id, ok) = settings.value("duoInput", 0).toInt()
			self.inputTypeButtonGroup.button(duo_input_id).setChecked(True)
