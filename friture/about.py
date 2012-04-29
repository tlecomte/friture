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
import datetime

major = 0
minor = 3
micro = 0
qualifier = ""
date = datetime.date(2012, 4, 29)

version = "%d.%d.%d%s" %(major, minor, micro, qualifier) if (micro > 0)  else "%d.%d%s" %(major, minor, qualifier)

aboutText = """
<p> <b>Friture %s</b> (dated %s)
<p> Friture is an application for real-time audio analysis.
<p> Written in Python, using PyQt, PyQwt, PyAudio and SciPy.
<p> License is GPLv3.
<p> Homepage: <a href="http://www.github.com/tlecomte/friture">http://www.github.com/tlecomte/friture</a>
<p> Send comments, ideas and bug reports to: <a href="mailto:lecomte.timothee@gmail.com">lecomte.timothee@gmail.com</a>
<p> Splash screen photo credit: <a href="http://www.flickr.com/photos/visual_dichotomy/3623619145/">visual.dichotomy</a> (CC BY 2.0)
""" %(version, date.isoformat())

class About_Dialog(QtGui.QDialog):
	def __init__(self, parent):
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
		
		self.tab_stats = QtGui.QWidget()
		self.tab_stats_layout = QtGui.QGridLayout(self.tab_stats)
		self.stats_scrollarea = QtGui.QScrollArea(self.tab_stats)		
		self.stats_scrollarea.setWidgetResizable(True)
		self.stats_scrollarea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
		self.stats_scrollarea.setObjectName("stats_scrollArea")
		self.scrollAreaWidgetContents = QtGui.QWidget(self.stats_scrollarea)
		self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 87, 220))
		self.scrollAreaWidgetContents.setStyleSheet("""QWidget { background: white }""")
		self.scrollAreaWidgetContents.setObjectName("stats_scrollAreaWidgetContents")
		self.stats_layout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
		self.stats_layout.setObjectName("stats_layout")
		self.LabelStats = QtGui.QLabel(self.scrollAreaWidgetContents)
		self.LabelStats.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
		self.LabelStats.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
		self.LabelStats.setObjectName("LabelStats")
		self.stats_layout.addWidget(self.LabelStats)
		self.stats_scrollarea.setWidget(self.scrollAreaWidgetContents)
		self.tab_stats_layout.addWidget(self.stats_scrollarea)
		self.tab_stats.setObjectName("tab_stats")
		self.tabWidget.addTab(self.tab_stats, "Statistics")
		
		self.tab_log = QtGui.QWidget()
		self.tab_log_layout = QtGui.QGridLayout(self.tab_log)
		self.log_scrollarea = QtGui.QScrollArea(self.tab_log)		
		self.log_scrollarea.setWidgetResizable(True)
		self.log_scrollarea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
		self.log_scrollarea.setObjectName("log_scrollArea")
		self.log_scrollAreaWidgetContents = QtGui.QWidget(self.log_scrollarea)
		self.log_scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 87, 220))
		self.log_scrollAreaWidgetContents.setStyleSheet("""QWidget { background: white }""")
		self.log_scrollAreaWidgetContents.setObjectName("log_scrollAreaWidgetContents")
		self.log_layout = QtGui.QVBoxLayout(self.log_scrollAreaWidgetContents)
		self.log_layout.setObjectName("log_layout")
		self.LabelLog = QtGui.QLabel(self.log_scrollAreaWidgetContents)
		self.LabelLog.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
		self.LabelLog.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
		self.LabelLog.setObjectName("LabelLog")
		self.log_layout.addWidget(self.LabelLog)
		self.log_scrollarea.setWidget(self.log_scrollAreaWidgetContents)
		self.tab_log_layout.addWidget(self.log_scrollarea)
		self.tab_log.setObjectName("tab_log")
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
