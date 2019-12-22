# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\settings.ui'
#
# Created: Sat Feb 14 20:44:20 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from . import friture_rc
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Settings_Dialog(object):

    def setupUi(self, Settings_Dialog):
        Settings_Dialog.setObjectName("Settings_Dialog")
        Settings_Dialog.resize(483, 275)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images-src/tools.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Settings_Dialog.setWindowIcon(icon)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(Settings_Dialog)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_inputType_2 = QtWidgets.QLabel(Settings_Dialog)
        self.label_inputType_2.setObjectName("label_inputType_2")
        self.verticalLayout_5.addWidget(self.label_inputType_2)
        self.comboBox_inputDevice = QtWidgets.QComboBox(Settings_Dialog)
        self.comboBox_inputDevice.setObjectName("comboBox_inputDevice")
        self.verticalLayout_5.addWidget(self.comboBox_inputDevice)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.label_inputType = QtWidgets.QLabel(Settings_Dialog)
        self.label_inputType.setObjectName("label_inputType")
        self.verticalLayout_3.addWidget(self.label_inputType)
        self.radioButton_single = QtWidgets.QRadioButton(Settings_Dialog)
        self.radioButton_single.setChecked(True)
        self.radioButton_single.setObjectName("radioButton_single")
        self.inputTypeButtonGroup = QtWidgets.QButtonGroup(Settings_Dialog)
        self.inputTypeButtonGroup.setObjectName("inputTypeButtonGroup")
        self.inputTypeButtonGroup.addButton(self.radioButton_single)
        self.verticalLayout_3.addWidget(self.radioButton_single)
        self.radioButton_duo = QtWidgets.QRadioButton(Settings_Dialog)
        self.radioButton_duo.setObjectName("radioButton_duo")
        self.inputTypeButtonGroup.addButton(self.radioButton_duo)
        self.verticalLayout_3.addWidget(self.radioButton_duo)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_first = QtWidgets.QGroupBox(Settings_Dialog)
        self.groupBox_first.setObjectName("groupBox_first")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_first)
        self.verticalLayout.setObjectName("verticalLayout")
        self.comboBox_firstChannel = QtWidgets.QComboBox(self.groupBox_first)
        self.comboBox_firstChannel.setObjectName("comboBox_firstChannel")
        self.verticalLayout.addWidget(self.comboBox_firstChannel)
        self.verticalLayout_4.addWidget(self.groupBox_first)
        self.groupBox_second = QtWidgets.QGroupBox(Settings_Dialog)
        self.groupBox_second.setEnabled(False)
        self.groupBox_second.setObjectName("groupBox_second")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_second)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.comboBox_secondChannel = QtWidgets.QComboBox(self.groupBox_second)
        self.comboBox_secondChannel.setObjectName("comboBox_secondChannel")
        self.verticalLayout_2.addWidget(self.comboBox_secondChannel)
        self.verticalLayout_4.addWidget(self.groupBox_second)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.verticalLayout_5.addLayout(self.horizontalLayout)

        self.retranslateUi(Settings_Dialog)
        QtCore.QMetaObject.connectSlotsByName(Settings_Dialog)

    def retranslateUi(self, Settings_Dialog):
        _translate = QtCore.QCoreApplication.translate
        Settings_Dialog.setWindowTitle(_translate("Settings_Dialog", "Settings"))
        self.label_inputType_2.setText(_translate("Settings_Dialog", "Select the input device :"))
        self.label_inputType.setText(_translate("Settings_Dialog", "Select the type of input :"))
        self.radioButton_single.setText(_translate("Settings_Dialog", "Single channel"))
        self.radioButton_duo.setText(_translate("Settings_Dialog", "Two channels"))
        self.groupBox_first.setTitle(_translate("Settings_Dialog", "First channel"))
        self.groupBox_second.setTitle(_translate("Settings_Dialog", "Second channel"))
