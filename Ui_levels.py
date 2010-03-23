# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'levels.ui'
#
# Created: Tue Mar 23 23:20:59 2010
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Levels_Widget(object):
    def setupUi(self, Levels_Widget):
        Levels_Widget.setObjectName("Levels_Widget")
        Levels_Widget.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(Levels_Widget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_rms = QtGui.QLabel(Levels_Widget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)
        self.label_rms.setFont(font)
        self.label_rms.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing)
        self.label_rms.setObjectName("label_rms")
        self.gridLayout.addWidget(self.label_rms, 0, 0, 1, 1)
        self.meter = qsynthMeter(Levels_Widget)
        self.meter.setStyleSheet("""qsynthMeter {
border: 1px solid gray;
border-radius: 2px;
padding: 1px;
}""")
        self.meter.setObjectName("meter")
        self.gridLayout.addWidget(self.meter, 0, 1, 2, 1)
        self.label_peak = QtGui.QLabel(Levels_Widget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)
        self.label_peak.setFont(font)
        self.label_peak.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_peak.setObjectName("label_peak")
        self.gridLayout.addWidget(self.label_peak, 0, 2, 1, 1)
        self.label_rms_legend = QtGui.QLabel(Levels_Widget)
        self.label_rms_legend.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.label_rms_legend.setObjectName("label_rms_legend")
        self.gridLayout.addWidget(self.label_rms_legend, 1, 0, 1, 1)
        self.label_peak_legend = QtGui.QLabel(Levels_Widget)
        self.label_peak_legend.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_peak_legend.setObjectName("label_peak_legend")
        self.gridLayout.addWidget(self.label_peak_legend, 1, 2, 1, 1)

        self.retranslateUi(Levels_Widget)
        QtCore.QMetaObject.connectSlotsByName(Levels_Widget)

    def retranslateUi(self, Levels_Widget):
        Levels_Widget.setWindowTitle(QtGui.QApplication.translate("Levels_Widget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rms.setText(QtGui.QApplication.translate("Levels_Widget", "-100.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_peak.setText(QtGui.QApplication.translate("Levels_Widget", "-100.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rms_legend.setText(QtGui.QApplication.translate("Levels_Widget", "dBFS\n"
"RMS", None, QtGui.QApplication.UnicodeUTF8))
        self.label_peak_legend.setText(QtGui.QApplication.translate("Levels_Widget", "dBFS\n"
"peak", None, QtGui.QApplication.UnicodeUTF8))

from qsynthmeter import qsynthMeter
