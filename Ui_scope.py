# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scope.ui'
#
# Created: Wed Mar 24 12:22:01 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Scope_Widget(object):
    def setupUi(self, Scope_Widget):
        Scope_Widget.setObjectName("Scope_Widget")
        Scope_Widget.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(Scope_Widget)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneUp = TimePlot(Scope_Widget)
        self.PlotZoneUp.setObjectName("PlotZoneUp")
        self.gridLayout.addWidget(self.PlotZoneUp, 0, 0, 1, 1)

        self.retranslateUi(Scope_Widget)
        QtCore.QMetaObject.connectSlotsByName(Scope_Widget)

    def retranslateUi(self, Scope_Widget):
        Scope_Widget.setWindowTitle(QtGui.QApplication.translate("Scope_Widget", "Form", None, QtGui.QApplication.UnicodeUTF8))

from timeplot import TimePlot
