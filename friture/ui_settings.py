# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings.ui'
#
# Created: Wed Jan 26 10:02:12 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Settings_Dialog(object):
    def setupUi(self, Settings_Dialog):
        Settings_Dialog.setObjectName("Settings_Dialog")
        Settings_Dialog.resize(257, 248)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images-src/tools.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Settings_Dialog.setWindowIcon(icon)
        self.formLayout = QtGui.QFormLayout(Settings_Dialog)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label_3 = QtGui.QLabel(Settings_Dialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_3)
        self.comboBox_inputDevice = QtGui.QComboBox(Settings_Dialog)
        self.comboBox_inputDevice.setObjectName("comboBox_inputDevice")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.comboBox_inputDevice)

        self.retranslateUi(Settings_Dialog)
        QtCore.QMetaObject.connectSlotsByName(Settings_Dialog)

    def retranslateUi(self, Settings_Dialog):
        Settings_Dialog.setWindowTitle(QtGui.QApplication.translate("Settings_Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Settings_Dialog", "Sound input", None, QtGui.QApplication.UnicodeUTF8))

import friture.friture_rc
