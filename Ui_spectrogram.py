# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'spectrogram.ui'
#
# Created: Fri Mar 26 16:19:35 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Spectrogram_Widget(object):
    def setupUi(self, Spectrogram_Widget):
        Spectrogram_Widget.setObjectName("Spectrogram_Widget")
        Spectrogram_Widget.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(Spectrogram_Widget)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneImage = ImagePlot(Spectrogram_Widget)
        self.PlotZoneImage.setObjectName("PlotZoneImage")
        self.gridLayout.addWidget(self.PlotZoneImage, 1, 1, 1, 1)
        self.pushButtonSettings = QtGui.QPushButton(Spectrogram_Widget)
        self.pushButtonSettings.setObjectName("pushButtonSettings")
        self.gridLayout.addWidget(self.pushButtonSettings, 0, 1, 1, 1)

        self.retranslateUi(Spectrogram_Widget)
        QtCore.QMetaObject.connectSlotsByName(Spectrogram_Widget)

    def retranslateUi(self, Spectrogram_Widget):
        Spectrogram_Widget.setWindowTitle(QtGui.QApplication.translate("Spectrogram_Widget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonSettings.setText(QtGui.QApplication.translate("Spectrogram_Widget", "Settings", None, QtGui.QApplication.UnicodeUTF8))

from imageplot import ImagePlot
