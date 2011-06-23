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

from PyQt4 import QtGui
from friture.ui_settings import Ui_Settings_Dialog

class Settings_Dialog(QtGui.QDialog, Ui_Settings_Dialog):
	def __init__(self, parent):
		QtGui.QDialog.__init__(self, parent)
		Ui_Settings_Dialog.__init__(self)
		
		# Setup the user interface
		self.setupUi(self)

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
