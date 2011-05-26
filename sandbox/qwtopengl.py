#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""PyQt4 port of the opengl/hellogl example from Qt v4.x"""

import sys

from PyQt4 import QtCore, QtGui, QtOpenGL
import PyQt4.Qwt5 as Qwt

try:
    from OpenGL import GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)

from numpy import arange, zeros, ones
from numpy.random import random

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.glPlotWidget = GLPlotWidget()

        plotLayout = QtGui.QGridLayout()
        plotLayout.addWidget(self.glPlotWidget, 0, 0)
        self.setLayout(plotLayout)

        self.setWindowTitle("Hello Qwt Numpy GL")

        self.i = 0

        self.animator = QtCore.QTimer()
        self.animator.setInterval(0)
        self.animator.timeout.connect(self.updatedata)
        self.animator.start()

    def updatedata(self):
        n = 1000
        
        w = 0.002
        h = 1.
        x = -1. + arange(n)*w
        y = (random(n)-0.5)*0.3 - 0.5
        
        c = random(n)
        
        self.glPlotWidget.setQuadData(x, y, w, h, c)
        
        self.i += 1
        if self.i % 25 == 0:
            print self.i


class GLPlotWidget(QtGui.QWidget):
    def __init__(self):
        super(GLPlotWidget, self).__init__()

        self.glWidget = GLWidget()

        self.verticalScaleEngine = Qwt.QwtLinearScaleEngine()

        self.verticalScale = Qwt.QwtScaleWidget(self)
        self.verticalScale.setTitle("PSD (dB)")
        self.verticalScale.setScaleDiv(self.verticalScaleEngine.transformation(),
                                  self.verticalScaleEngine.divideScale(0., 100., 8, 5))
        self.verticalScale.setMargin(0)

        self.horizontalScaleEngine = Qwt.QwtLinearScaleEngine()

        self.horizontalScale = Qwt.QwtScaleWidget(self)
        self.horizontalScale.setTitle("Frequency (Hz)")
        self.horizontalScale.setScaleDiv(self.horizontalScaleEngine.transformation(),
                                  self.horizontalScaleEngine.divideScale(0., 100., 8, 5))
        self.horizontalScale.setAlignment(Qwt.QwtScaleDraw.BottomScale)
        self.horizontalScale.setMargin(0)
        #self.horizontalScale.setBorderDist(0,0)
        self.horizontalScale.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)

        left = self.horizontalScale.getBorderDistHint()[0]
        right = self.horizontalScale.getBorderDistHint()[1]
        top = self.verticalScale.getBorderDistHint()[0]
        bottom = self.verticalScale.getBorderDistHint()[1]

        plotLayout = QtGui.QGridLayout()
        plotLayout.setSpacing(0)
        plotLayout.addWidget(self.verticalScale, 0, 0, 3, 1)
        plotLayout.addWidget(self.glWidget, 1, 2)
        plotLayout.addWidget(self.horizontalScale, 3, 1, 1, 3)
        plotLayout.setRowMinimumHeight(0, top)
        plotLayout.setRowMinimumHeight(2, bottom-1)
        plotLayout.setColumnMinimumWidth(1, left)
        plotLayout.setColumnMinimumWidth(3, right)
        
        self.setLayout(plotLayout)

    def setlogfreqscale(self):
        return

    def setfreqrange(self, minfreq, maxfreq):
        return

    def setspecrange(self, spec_min, spec_max):
        return
    
    def setweighting(self, weighting):
        return
    
    def setdata(self, freq, db_spectrogram):
        return
        
    def setQuadData(self, x, y, w, h, colors):
        n = x.shape[0]
    
        vertex = zeros((n,4,2))
        vertex[:,0,0] = x
        vertex[:,0,1] = y + h
        vertex[:,1,0] = x + w
        vertex[:,1,1] = y + h
        vertex[:,2,0] = x + w
        vertex[:,2,1] = y
        vertex[:,3,0] = x
        vertex[:,3,1] = y

        color = ones((n,4,3))
        color[:,0,1] = colors
        color[:,1,1] = colors
        color[:,2,1] = colors
        color[:,3,1] = colors
        color[:,0,2] = colors
        color[:,1,2] = colors
        color[:,2,2] = colors
        color[:,3,2] = colors
        
        self.glWidget.setQuadData(vertex, color)


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        self.lastPos = QtCore.QPoint()

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def initializeGL(self):
        GL.glShadeModel(GL.GL_FLAT)
        GL.glDepthFunc(GL.GL_LESS) # The Type Of Depth Test To Do
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        #GL.glEnable(GL.GL_CULL_FACE)

    def setQuadData(self, vertices, colors):
        self.n = vertices.shape[0]
        
        GL.glVertexPointerd(vertices)
        GL.glColorPointerd(colors)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        
        self.updateGL()

    def paintGL(self):
        # Clear The Screen And The Depth Buffer
        #GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        # Reset The View
        GL.glLoadIdentity()
        
        GL.glClearColor(1, 1, 1, 0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        #GL.glOrtho(-1, 1, -1, 1, -1, 1)
        #GL.glDisable(GL.GL_LIGHTING)
        GL.glDrawArrays(GL.GL_QUADS, 0, 4*self.n)
        #GL.glEnable(GL.GL_LIGHTING)

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return
        
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        #dx = event.x() - self.lastPos.x()
        #dy = event.y() - self.lastPos.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            print "left"
        elif event.buttons() & QtCore.Qt.RightButton:
            print "right"

        self.lastPos = event.pos()


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
