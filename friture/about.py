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

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import sounddevice
import numpy
import OpenGL
import friture.friture_rc
import friture
from friture.statisticswidget import StatisticsWidget

aboutText = """
<p> <b>Friture %s</b> (dated %s)</p>
<p> Friture is an application for real-time audio analysis.</p>
<p> License is GPLv3.</p>
<p> Homepage: <a href="http://friture.org">http://friture.org</a></p>
<p> <a href="http://friture.org/privacy.html">Privacy Policy</a></p>
<p> Send comments, ideas and bug reports to: <a href="mailto:contact@friture.org">contact@friture.org</a></p>
<p> Splash screen photo credit: <a href="http://www.flickr.com/photos/visual_dichotomy/3623619145/">visual.dichotomy</a> (CC BY 2.0)</p>
<p>This instance of Friture runs thanks to the following external projects:</p>

<ul>
        <li>Python %s</li>
        <li>PyQt %s (Qt %s)</li>
        <li>Python-sounddevice %s (%s)</li>
        <li>Numpy %s</li>
        <li>Cython</li>
        <li>PyOpenGL %s</li>
</ul>
""" % (friture.__version__,
       friture.__releasedate__,
       "%d.%d" % (sys.version_info.major, sys.version_info.minor),
       QtCore.PYQT_VERSION_STR,
       QtCore.qVersion(),
       sounddevice.__version__,
       sounddevice.get_portaudio_version()[1],
       numpy.__version__,
       # Cython.__version__, #this pulls the whole Cython, makes PyInstaller think it needs all the dependencies, even IPython!
       OpenGL.__version__)


class About_Dialog(QtWidgets.QDialog):

    def __init__(self, parent, timer):
        super().__init__(parent)

        self.setObjectName("About_Dialog")
        self.resize(400, 300)
        self.setWindowTitle("About Friture")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images-src/window-icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        self.aboutTab = QtWidgets.QWidget()
        self.aboutTab.setObjectName("aboutTab")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.aboutTab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.aboutTab)
        self.label_2.setMinimumSize(QtCore.QSize(128, 128))
        self.label_2.setMaximumSize(QtCore.QSize(128, 128))
        self.label_2.setPixmap(QtGui.QPixmap(":/images-src/window-icon.svg"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.aboutTab)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName("label")
        self.label.setText(aboutText)

        self.horizontalLayout.addWidget(self.label)
        self.tabWidget.addTab(self.aboutTab, "About")

        self.tab_stats = StatisticsWidget(self, timer)
        self.tabWidget.addTab(self.tab_stats, "Statistics")

        self.tabWidget.setCurrentIndex(0)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")

        self.verticalLayout.addWidget(self.tabWidget)
        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
