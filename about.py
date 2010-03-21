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
from Ui_about import Ui_About_Dialog

class About_Dialog(QtGui.QDialog, Ui_About_Dialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		Ui_About_Dialog.__init__(self)
		
		# Setup the user interface
		self.setupUi(self)
		
		aboutText = u"Friture is an application for real-time audio analysis.\n" \
		"Written in Python\n" \
		"License GPLv3\n" \
		"By Timothee Lecomte\n" \
		"Homepage: http://www.github.com/tlecomte/friture"
		
		self.label.setText(aboutText)