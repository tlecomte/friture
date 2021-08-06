#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################################################################
##
## Copyright (C) 2006-2006 Trolltech ASA. All rights reserved.
##
## This file is part of the example classes of the Qt Toolkit.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following information to ensure GNU
## General Public Licensing requirements will be met:
## http://www.trolltech.com/products/qt/opensource.html
##
## If you are unsure which license is appropriate for your use, please
## review the following information:
## http://www.trolltech.com/products/qt/licensing.html or contact the
## sales department at sales@trolltech.com.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

import sys
import math

from PyQt4 import QtCore, QtGui, QtOpenGL
from OpenGL import GL

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent):
	fmt = QtOpenGL.QGLFormat()
	fmt.setSampleBuffers(True) # antialiasing
        QtOpenGL.QGLWidget.__init__(self, fmt, parent)

        self.setFixedSize(300, 300)
        self.setAutoFillBackground(False)
	self.textPen = QtGui.QPen(QtCore.Qt.white)
        self.textFont = QtGui.QFont()
        self.textFont.setPixelSize(50)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(150, 150)
        painter.setPen(self.textPen)
        painter.setFont(self.textFont)
        painter.drawText(QtCore.QRect(-50, -50, 100, 100), QtCore.Qt.AlignCenter, "Qt")


class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        openGL = GLWidget(self)

        layout = QtGui.QGridLayout()
        layout.addWidget(openGL, 0, 1)
        self.setLayout(layout)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
