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
import friture.friture_rc
import friture
from friture.logwidget import LogWidget
from friture.statisticswidget import StatisticsWidget

aboutText = """
<p> <b>Friture %s</b> (dated %s)
<p> Friture is an application for real-time audio analysis.
<p> Written in Python, using PyQt, PyAudio, Numpy, SciPy, Cython, OpenGL.
<p> License is GPLv3.
<p> Homepage: <a href="http://friture.org">http://friture.org</a>
<p> Send comments, ideas and bug reports to: <a href="mailto:contact@friture.org">contact@friture.org</a>
<p> Splash screen photo credit: <a href="http://www.flickr.com/photos/visual_dichotomy/3623619145/">visual.dichotomy</a> (CC BY 2.0)
""" %(friture.__version__, friture.__releasedate__)

class About_Dialog(QtGui.QDialog):
	def __init__(self, parent, logger, audiobackend, timer):
		QtGui.QDialog.__init__(self, parent)

		self.setObjectName("About_Dialog")
		self.resize(400, 300)
		self.setWindowTitle("About Friture")
		
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/images-src/window-icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
		self.label_2.setPixmap(QtGui.QPixmap(":/images-src/window-icon.svg"))
		self.label_2.setScaledContents(True)
		self.label_2.setObjectName("label_2")
		self.horizontalLayout.addWidget(self.label_2)
		self.label = QtGui.QLabel(self.aboutTab)
		self.label.setOpenExternalLinks( True ) 
		self.label.setObjectName("label")
		self.label.setText(aboutText)
		
		self.horizontalLayout.addWidget(self.label)
		self.tabWidget.addTab(self.aboutTab, "About")
		
		self.tab_stats = StatisticsWidget(self, logger, timer, audiobackend)
		self.tabWidget.addTab(self.tab_stats, "Statistics")
		
		self.tab_log = LogWidget(self, logger)
		self.tabWidget.addTab(self.tab_log, "Log")
		
		self.tabWidget.setCurrentIndex(0)
		
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
		self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
		self.buttonBox.setObjectName("buttonBox")
		
		self.verticalLayout.addWidget(self.tabWidget)
		self.verticalLayout.addWidget(self.buttonBox)
		
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
		QtCore.QMetaObject.connectSlotsByName(self)


