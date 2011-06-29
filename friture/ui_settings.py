# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings.ui'
#
# Created: Wed Jun 29 22:32:23 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Settings_Dialog(object):
    def setupUi(self, Settings_Dialog):
        Settings_Dialog.setObjectName(_fromUtf8("Settings_Dialog"))
        Settings_Dialog.resize(470, 275)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images-src/tools.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Settings_Dialog.setWindowIcon(icon)
        self.verticalLayout_5 = QtGui.QVBoxLayout(Settings_Dialog)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.label_inputType_2 = QtGui.QLabel(Settings_Dialog)
        self.label_inputType_2.setObjectName(_fromUtf8("label_inputType_2"))
        self.verticalLayout_5.addWidget(self.label_inputType_2)
        self.comboBox_inputDevice = QtGui.QComboBox(Settings_Dialog)
        self.comboBox_inputDevice.setObjectName(_fromUtf8("comboBox_inputDevice"))
        self.verticalLayout_5.addWidget(self.comboBox_inputDevice)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.label_inputType = QtGui.QLabel(Settings_Dialog)
        self.label_inputType.setObjectName(_fromUtf8("label_inputType"))
        self.verticalLayout_3.addWidget(self.label_inputType)
        self.radioButton_single = QtGui.QRadioButton(Settings_Dialog)
        self.radioButton_single.setChecked(True)
        self.radioButton_single.setObjectName(_fromUtf8("radioButton_single"))
        self.inputTypeButtonGroup = QtGui.QButtonGroup(Settings_Dialog)
        self.inputTypeButtonGroup.setObjectName(_fromUtf8("inputTypeButtonGroup"))
        self.inputTypeButtonGroup.addButton(self.radioButton_single)
        self.verticalLayout_3.addWidget(self.radioButton_single)
        self.radioButton_duo = QtGui.QRadioButton(Settings_Dialog)
        self.radioButton_duo.setObjectName(_fromUtf8("radioButton_duo"))
        self.inputTypeButtonGroup.addButton(self.radioButton_duo)
        self.verticalLayout_3.addWidget(self.radioButton_duo)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.groupBox_first = QtGui.QGroupBox(Settings_Dialog)
        self.groupBox_first.setObjectName(_fromUtf8("groupBox_first"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_first)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.comboBox_firstChannel = QtGui.QComboBox(self.groupBox_first)
        self.comboBox_firstChannel.setObjectName(_fromUtf8("comboBox_firstChannel"))
        self.verticalLayout.addWidget(self.comboBox_firstChannel)
        self.verticalLayout_4.addWidget(self.groupBox_first)
        self.groupBox_second = QtGui.QGroupBox(Settings_Dialog)
        self.groupBox_second.setEnabled(False)
        self.groupBox_second.setObjectName(_fromUtf8("groupBox_second"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_second)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.comboBox_secondChannel = QtGui.QComboBox(self.groupBox_second)
        self.comboBox_secondChannel.setObjectName(_fromUtf8("comboBox_secondChannel"))
        self.verticalLayout_2.addWidget(self.comboBox_secondChannel)
        self.verticalLayout_4.addWidget(self.groupBox_second)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.label_delay = QtGui.QLabel(Settings_Dialog)
        self.label_delay.setEnabled(False)
        self.label_delay.setObjectName(_fromUtf8("label_delay"))
        self.verticalLayout_5.addWidget(self.label_delay)
        self.doubleSpinBox_delay = QtGui.QDoubleSpinBox(Settings_Dialog)
        self.doubleSpinBox_delay.setEnabled(False)
        self.doubleSpinBox_delay.setDecimals(2)
        self.doubleSpinBox_delay.setMinimum(-10000.0)
        self.doubleSpinBox_delay.setMaximum(10000.0)
        self.doubleSpinBox_delay.setSingleStep(100.0)
        self.doubleSpinBox_delay.setObjectName(_fromUtf8("doubleSpinBox_delay"))
        self.verticalLayout_5.addWidget(self.doubleSpinBox_delay)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem3)

        self.retranslateUi(Settings_Dialog)
        QtCore.QMetaObject.connectSlotsByName(Settings_Dialog)

    def retranslateUi(self, Settings_Dialog):
        Settings_Dialog.setWindowTitle(QtGui.QApplication.translate("Settings_Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label_inputType_2.setText(QtGui.QApplication.translate("Settings_Dialog", "Select the input device :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_inputType.setText(QtGui.QApplication.translate("Settings_Dialog", "Select the type of input :", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_single.setText(QtGui.QApplication.translate("Settings_Dialog", "Single channel", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_duo.setText(QtGui.QApplication.translate("Settings_Dialog", "Two channels", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_first.setTitle(QtGui.QApplication.translate("Settings_Dialog", "First channel", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_second.setTitle(QtGui.QApplication.translate("Settings_Dialog", "Second channel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_delay.setText(QtGui.QApplication.translate("Settings_Dialog", "Choose a time delay for difference measurement between the two channels (second minus first):", None, QtGui.QApplication.UnicodeUTF8))
        self.doubleSpinBox_delay.setSuffix(QtGui.QApplication.translate("Settings_Dialog", " ms", None, QtGui.QApplication.UnicodeUTF8))

import friture_rc
