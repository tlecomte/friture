#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth�e Lecomte

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
import resource_rc

class About_Dialog(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		
		self.setObjectName("About_Dialog")
		self.resize(400, 300)
		self.setWindowTitle("About Friture")
		
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/window-icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.setWindowIcon(icon)
		
		self.verticalLayout = QtGui.QVBoxLayout(self)
		self.verticalLayout.setObjectName("verticalLayout")
		
		self.tabWidget = QtGui.QTabWidget(self)
		self.tabWidget.setObjectName("tabWidget")
		
		self.aboutTab = QtGui.QWidget()
		self.aboutTab.setObjectName("aboutTab")
		self.horizontalLayout = QtGui.QHBoxLayout(self.aboutTab)
		self.horizontalLayout.setObjectName("horizontalLayout")
		self.label_2 = QtGui.QLabel(self.aboutTab)
		self.label_2.setMinimumSize(QtCore.QSize(128, 128))
		self.label_2.setMaximumSize(QtCore.QSize(128, 128))
		self.label_2.setPixmap(QtGui.QPixmap(":/window-icon.svg"))
		self.label_2.setScaledContents(True)
		self.label_2.setObjectName("label_2")
		self.horizontalLayout.addWidget(self.label_2)
		self.label = QtGui.QLabel(self.aboutTab)
		self.label.setObjectName("label")
		aboutText = u"Friture is an application for real-time audio analysis.\n" \
		"Written in Python\n" \
		"License GPLv3\n" \
		"By Timothee Lecomte\n" \
		"Homepage: http://www.github.com/tlecomte/friture"
		self.label.setText(aboutText)
		self.horizontalLayout.addWidget(self.label)
		self.tabWidget.addTab(self.aboutTab, "About")
		
		#self.tab_2 = QtGui.QWidget()
		#self.tab_2.setObjectName("tab_2")
		#self.tabWidget.addTab(self.tab_2, "Tab 2")
		#self.tabWidget.setCurrentIndex(0)
		
		self.verticalLayout.addWidget(self.tabWidget)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
		self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
		self.buttonBox.setObjectName("buttonBox")
		self.verticalLayout.addWidget(self.buttonBox)

		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
		QtCore.QMetaObject.connectSlotsByName(self)
