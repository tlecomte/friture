# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'friture.ui'
#
# Created: Wed Mar 17 18:37:17 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(869, 573)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/window-icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.PlotZoneImage = ImagePlot(self.centralwidget)
        self.PlotZoneImage.setStyleSheet("QwtPlotCanvas {\n"
"}")
        self.PlotZoneImage.setObjectName("PlotZoneImage")
        self.gridLayout_3.addWidget(self.PlotZoneImage, 0, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.dockWidgetLevels = QtGui.QDockWidget(MainWindow)
        self.dockWidgetLevels.setObjectName("dockWidgetLevels")
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout_4 = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.frame_3 = QtGui.QFrame(self.dockWidgetContents)
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout_8 = QtGui.QGridLayout(self.frame_3)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_rms = QtGui.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)
        self.label_rms.setFont(font)
        self.label_rms.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing)
        self.label_rms.setObjectName("label_rms")
        self.gridLayout_8.addWidget(self.label_rms, 0, 0, 1, 1)
        self.meter = qsynthMeter(self.frame_3)
        self.meter.setStyleSheet("qsynthMeter {\n"
"border: 1px solid gray;\n"
"border-radius: 2px;\n"
"padding: 1px;\n"
"}")
        self.meter.setObjectName("meter")
        self.gridLayout_8.addWidget(self.meter, 0, 1, 2, 1)
        self.label_peak = QtGui.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)
        self.label_peak.setFont(font)
        self.label_peak.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_peak.setObjectName("label_peak")
        self.gridLayout_8.addWidget(self.label_peak, 0, 2, 1, 1)
        self.label_rms_legend = QtGui.QLabel(self.frame_3)
        self.label_rms_legend.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.label_rms_legend.setObjectName("label_rms_legend")
        self.gridLayout_8.addWidget(self.label_rms_legend, 1, 0, 1, 1)
        self.label_peak_legend = QtGui.QLabel(self.frame_3)
        self.label_peak_legend.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_peak_legend.setObjectName("label_peak_legend")
        self.gridLayout_8.addWidget(self.label_peak_legend, 1, 2, 1, 1)
        self.gridLayout_4.addWidget(self.frame_3, 0, 0, 1, 1)
        self.dockWidgetLevels.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidgetLevels)
        self.dockWidgetStatistics = QtGui.QDockWidget(MainWindow)
        self.dockWidgetStatistics.setObjectName("dockWidgetStatistics")
        self.dockWidgetContents_2 = QtGui.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.gridLayout_2 = QtGui.QGridLayout(self.dockWidgetContents_2)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.scrollArea = QtGui.QScrollArea(self.dockWidgetContents_2)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 150, 128))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LabelLevel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.LabelLevel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.LabelLevel.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.LabelLevel.setObjectName("LabelLevel")
        self.verticalLayout.addWidget(self.LabelLevel)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.dockWidgetStatistics.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidgetStatistics)
        self.dockWidgetScope = QtGui.QDockWidget(MainWindow)
        self.dockWidgetScope.setStyleSheet("QwtPlotCanvas {\n"
"  border: 1px solid gray;\n"
" border-radius: 2px;\n"
"  background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"stop: 0 #AAAAAA, stop: 0.3 #FFFFFF);\n"
"}")
        self.dockWidgetScope.setObjectName("dockWidgetScope")
        self.dockWidgetContents_4 = QtGui.QWidget()
        self.dockWidgetContents_4.setObjectName("dockWidgetContents_4")
        self.gridLayout_5 = QtGui.QGridLayout(self.dockWidgetContents_4)
        self.gridLayout_5.setMargin(0)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.frame = QtGui.QFrame(self.dockWidgetContents_4)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setObjectName("frame")
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneUp = TimePlot(self.frame)
        self.PlotZoneUp.setObjectName("PlotZoneUp")
        self.gridLayout.addWidget(self.PlotZoneUp, 0, 0, 1, 1)
        self.gridLayout_5.addWidget(self.frame, 0, 0, 1, 1)
        self.dockWidgetScope.setWidget(self.dockWidgetContents_4)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(4), self.dockWidgetScope)
        self.dockWidgetSpectrum = QtGui.QDockWidget(MainWindow)
        self.dockWidgetSpectrum.setStyleSheet("QwtPlotCanvas {\n"
"  border: 1px solid gray;\n"
" border-radius: 2px;\n"
"  background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"stop: 0 #AAAAAA, stop: 0.3 #FFFFFF);\n"
"}")
        self.dockWidgetSpectrum.setObjectName("dockWidgetSpectrum")
        self.dockWidgetContents_5 = QtGui.QWidget()
        self.dockWidgetContents_5.setObjectName("dockWidgetContents_5")
        self.gridLayout_6 = QtGui.QGridLayout(self.dockWidgetContents_5)
        self.gridLayout_6.setMargin(0)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.frame_2 = QtGui.QFrame(self.dockWidgetContents_5)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_7 = QtGui.QGridLayout(self.frame_2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.PlotZoneSpect = SpectPlot(self.frame_2)
        self.PlotZoneSpect.setObjectName("PlotZoneSpect")
        self.gridLayout_7.addWidget(self.PlotZoneSpect, 0, 0, 1, 1)
        self.gridLayout_6.addWidget(self.frame_2, 0, 0, 1, 1)
        self.dockWidgetSpectrum.setWidget(self.dockWidgetContents_5)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(4), self.dockWidgetSpectrum)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setStyleSheet("QToolBar {\n"
"border: none;\n"
"background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"stop: 0 #a6a6a6, stop: 0.08 #7f7f7f,\n"
"stop: 0.39999 #717171, stop: 0.4 #626262,\n"
"stop: 0.9 #4c4c4c, stop: 1 #333333);\n"
"}\n"
"\n"
"QToolButton {\n"
"color: white;\n"
"}\n"
"")
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.dockWidgetLog = QtGui.QDockWidget(MainWindow)
        self.dockWidgetLog.setObjectName("dockWidgetLog")
        self.dockWidgetContents_3 = QtGui.QWidget()
        self.dockWidgetContents_3.setObjectName("dockWidgetContents_3")
        self.gridLayout_9 = QtGui.QGridLayout(self.dockWidgetContents_3)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.scrollArea_2 = QtGui.QScrollArea(self.dockWidgetContents_3)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtGui.QWidget(self.scrollArea_2)
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 142, 64))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.gridLayout_10 = QtGui.QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.LabelLog = QtGui.QLabel(self.scrollAreaWidgetContents_2)
        self.LabelLog.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.LabelLog.setObjectName("LabelLog")
        self.gridLayout_10.addWidget(self.LabelLog, 0, 0, 1, 1)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.gridLayout_9.addWidget(self.scrollArea_2, 0, 0, 1, 1)
        self.dockWidgetLog.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidgetLog)
        self.actionStart = QtGui.QAction(MainWindow)
        self.actionStart.setCheckable(True)
        self.actionStart.setChecked(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/stop.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/start.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon1.addPixmap(QtGui.QPixmap(":/start.svg"), QtGui.QIcon.Active, QtGui.QIcon.On)
        icon1.addPixmap(QtGui.QPixmap(":/start.svg"), QtGui.QIcon.Selected, QtGui.QIcon.On)
        icon1.addPixmap(QtGui.QPixmap(":/start.svg"), QtGui.QIcon.Disabled, QtGui.QIcon.On)
        self.actionStart.setIcon(icon1)
        self.actionStart.setObjectName("actionStart")
        self.actionSettings = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/tools.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSettings.setIcon(icon2)
        self.actionSettings.setObjectName("actionSettings")
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setIcon(icon2)
        self.actionAbout.setObjectName("actionAbout")
        self.toolBar.addAction(self.actionStart)
        self.toolBar.addAction(self.actionSettings)
        self.toolBar.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Friture", None, QtGui.QApplication.UnicodeUTF8))
        MainWindow.setStyleSheet(QtGui.QApplication.translate("MainWindow", "QToolBar {\n"
"border: none;\n"
"background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"stop: 0 #a6a6a6, stop: 0.08 #7f7f7f,\n"
"stop: 0.39999 #717171, stop: 0.4 #626262,\n"
"stop: 0.9 #4c4c4c, stop: 1 #333333);\n"
" }", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidgetLevels.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Input levels", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rms.setText(QtGui.QApplication.translate("MainWindow", "-100.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_peak.setText(QtGui.QApplication.translate("MainWindow", "-100.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rms_legend.setText(QtGui.QApplication.translate("MainWindow", "dBFS\n"
"RMS", None, QtGui.QApplication.UnicodeUTF8))
        self.label_peak_legend.setText(QtGui.QApplication.translate("MainWindow", "dBFS\n"
"peak", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidgetStatistics.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Statistics", None, QtGui.QApplication.UnicodeUTF8))
        self.LabelLevel.setText(QtGui.QApplication.translate("MainWindow", "No statistics", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidgetScope.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Scope", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidgetSpectrum.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Spectrum", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidgetLog.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Log", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStart.setText(QtGui.QApplication.translate("MainWindow", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStart.setToolTip(QtGui.QApplication.translate("MainWindow", "Start/Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSettings.setText(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSettings.setToolTip(QtGui.QApplication.translate("MainWindow", "Display settings dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))

from timeplot import TimePlot
from qsynthmeter import qsynthMeter
from imageplot import ImagePlot
from spectplot import SpectPlot
import resource_rc
