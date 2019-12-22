# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\friture.ui'
#
# Created: Sat Feb 14 20:44:29 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from . import friture_rc
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(869, 573)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images-src/window-icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionStart = QtWidgets.QAction(MainWindow)
        self.actionStart.setCheckable(True)
        self.actionStart.setChecked(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon1.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Disabled, QtGui.QIcon.On)
        icon1.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Selected, QtGui.QIcon.On)
        icon1.addPixmap(QtGui.QPixmap(":/images-src/start.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/images-src/stop.svg"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.actionStart.setIcon(icon1)
        self.actionStart.setObjectName("actionStart")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images-src/tools.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSettings.setIcon(icon2)
        self.actionSettings.setObjectName("actionSettings")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setIcon(icon)
        self.actionAbout.setObjectName("actionAbout")
        self.actionNew_dock = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/images-src/new-dock.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNew_dock.setIcon(icon3)
        self.actionNew_dock.setObjectName("actionNew_dock")
        self.toolBar.addAction(self.actionStart)
        self.toolBar.addAction(self.actionNew_dock)
        self.toolBar.addAction(self.actionSettings)
        self.toolBar.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Friture"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionStart.setText(_translate("MainWindow", "Stop"))
        self.actionStart.setToolTip(_translate("MainWindow", "Start/Stop"))
        self.actionStart.setShortcut(_translate("MainWindow", "Space"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))
        self.actionSettings.setToolTip(_translate("MainWindow", "Display settings dialog"))
        self.actionAbout.setText(_translate("MainWindow", "About Friture"))
        self.actionNew_dock.setText(_translate("MainWindow", "New dock"))
        self.actionNew_dock.setToolTip(_translate("MainWindow", "Add a new dock to Friture window"))
