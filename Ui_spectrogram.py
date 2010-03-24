# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'spectrogram.ui'
#
# Created: Wed Mar 24 15:58:35 2010
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
        self.gridLayout.addWidget(self.PlotZoneImage, 0, 0, 1, 1)

        self.retranslateUi(Spectrogram_Widget)
        QtCore.QMetaObject.connectSlotsByName(Spectrogram_Widget)

    def retranslateUi(self, Spectrogram_Widget):
        Spectrogram_Widget.setWindowTitle(QtGui.QApplication.translate("Spectrogram_Widget", "Form", None, QtGui.QApplication.UnicodeUTF8))

from imageplot import ImagePlot
