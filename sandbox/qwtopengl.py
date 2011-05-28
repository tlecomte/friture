#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""PyQt4 port of the opengl/hellogl example from Qt v4.x"""

import sys

from PyQt4 import QtCore, QtGui, QtOpenGL, Qt
import PyQt4.Qwt5 as Qwt

try:
    from OpenGL import GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)

from numpy import arange, zeros, ones, log10, ones, hstack
from numpy.random import random

# The peak decay rates (magic goes here :).
PEAK_DECAY_RATE = 1.0 - 3E-6
# Number of cycles the peak stays on hold before fall-off.
PEAK_FALLOFF_COUNT = 32 # default : 16

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
    def __init__(self, parent=None, logger=None):
        super(GLPlotWidget, self).__init__()

        self.glWidget = GLWidget()
        
        self.xmin = 0.
        self.xmax = 1.
        self.ymin = 0.
        self.ymax = 1.
        
        self.peak = zeros((1,))
        self.peak_int = 0
        self.peak_decay = PEAK_DECAY_RATE

        self.verticalScaleEngine = Qwt.QwtLinearScaleEngine()

        self.verticalScale = Qwt.QwtScaleWidget(self)
        self.verticalScale.setTitle("PSD (dB)")
        self.verticalScale.setScaleDiv(self.verticalScaleEngine.transformation(),
                                  self.verticalScaleEngine.divideScale(self.ymin, self.ymax, 8, 5))
        self.verticalScale.setMargin(0)

        self.logx = False
        self.horizontalScaleEngine = Qwt.QwtLinearScaleEngine()

        self.horizontalScale = Qwt.QwtScaleWidget(self)
        self.horizontalScale.setTitle("Frequency (Hz)")
        self.horizontalScale.setScaleDiv(self.horizontalScaleEngine.transformation(),
                                  self.horizontalScaleEngine.divideScale(self.xmin, self.xmax, 8, 5))
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

    def setlinfreqscale(self):
        self.logx = False
        self.horizontalScaleEngine = Qwt.QwtLinearScaleEngine()
        self.horizontalScale.setScaleDiv(self.horizontalScaleEngine.transformation(),
                                  self.horizontalScaleEngine.divideScale(self.xmin, self.xmax, 8, 5))

    def setlogfreqscale(self):
        self.logx = True
        self.horizontalScaleEngine = Qwt.QwtLog10ScaleEngine()
        self.horizontalScale.setScaleDiv(self.horizontalScaleEngine.transformation(),
                                  self.horizontalScaleEngine.divideScale(self.xmin, self.xmax, 8, 5))

    def setfreqrange(self, minfreq, maxfreq):
        self.xmin = minfreq
        self.xmax = maxfreq
        self.horizontalScale.setScaleDiv(self.horizontalScaleEngine.transformation(),
                                  self.horizontalScaleEngine.divideScale(self.xmin, self.xmax, 8, 5))

    def setspecrange(self, spec_min, spec_max):
        self.ymin = spec_min
        self.ymax = spec_max
        self.verticalScale.setScaleDiv(self.verticalScaleEngine.transformation(),
                                  self.verticalScaleEngine.divideScale(self.ymin, self.ymax, 8, 5))
    
    def setweighting(self, weighting):
        return
    
    def setdata(self, x, y):
        x1 = zeros(x.shape)
        x2 = zeros(x.shape)
        x1[0] = 1e-10
        x1[1:] = (x[1:] + x[:-1])/2.
        x2[:-1] = x1[1:]
        x2[-1] = 22050.
        
        if self.logx:
            transformed_x1 = (log10(x1/self.xmin))*2./(log10(self.xmax/self.xmin)) - 1.
            transformed_x2 = (log10(x2/self.xmin))*2./(log10(self.xmax/self.xmin)) - 1.    
        else:
            transformed_x1 = (x1 - self.xmin)*2./(self.xmax - self.xmin) - 1.
            transformed_x2 = (x2 - self.xmin)*2./(self.xmax - self.xmin) - 1.
        
        #transformed_db = self.verticalScaleEngine.transformation().xForm(db_spectrogram, self.ymin, self.ymax, 0., self.glWidget.height())
        transformed_y = (y - self.ymin)*2./(self.ymax - self.ymin) - 1.

        self.compute_peaks(transformed_y)
        
        Ones = ones(x.shape)
        
        x1_with_peaks = hstack((transformed_x1, transformed_x1))
        x2_with_peaks = hstack((transformed_x2, transformed_x2))
        y_with_peaks = hstack((transformed_y, self.peak))
        r_with_peaks = hstack((0.*Ones, 1.*Ones))
        g_with_peaks = hstack((0.5*Ones, 1. - self.peak_int))
        b_with_peaks = hstack((0.*Ones, 1. - self.peak_int))
        
        color = QtGui.QColor(Qt.Qt.darkGreen)
        print color.red(), color.green(), color.blue()
        
        #self.setQuadData(transformed_x1, transformed_y - 2., transformed_x2 - transformed_x1, 2., c)
        self.setQuadData(x1_with_peaks, y_with_peaks - 2., x2_with_peaks - x1_with_peaks, 2., r_with_peaks, g_with_peaks, b_with_peaks)
        
        #xMajorTick = self.horizontalScaleEngine.divideScale(self.xmin, self.xmax, 8, 5).ticks(2)
        #xMinorTick = self.horizontalScaleEngine.divideScale(self.xmin, self.xmax, 8, 5).ticks(0)
        
        # TODO :
        # - major/minor X/Y grid
        # - gradient styled background
        # - fix margins around the canvas
        # - pixel mean when band size < pixel size (mean != banding, on purpose)
        # - optimize if further needed, but last point should be more than enough !

    def compute_peaks(self, y):
        if len(self.peak) <> len(y):
            y_ones = ones(y.shape)
            self.peak = y_ones*(-500.)
            self.peak_int = zeros(y.shape)
            self.peak_decay = y_ones * 20. * log10(PEAK_DECAY_RATE) * 5000

        mask1 = (self.peak < y)
        mask2 = (-mask1)
        mask2_a = mask2 * (self.peak_int < 0.2)
        mask2_b = mask2 * (self.peak_int >= 0.2)

        self.peak[mask1] = y[mask1]
        self.peak[mask2_a] = self.peak[mask2_a] + self.peak_decay[mask2_a]
		
        self.peak_decay[mask1] = 20. * log10(PEAK_DECAY_RATE) * 5000
        self.peak_decay[mask2_a] += 20. * log10(PEAK_DECAY_RATE) * 5000

        self.peak_int[mask1] = 1.
        self.peak_int[mask2_b] *= 0.975
  
    def setQuadData(self, x, y, w, h, r, g, b):
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

        color = zeros((n,4,3))
        color[:,0,0] = r
        color[:,1,0] = r
        color[:,2,0] = r
        color[:,3,0] = r
        color[:,0,1] = g
        color[:,1,1] = g
        color[:,2,1] = g
        color[:,3,1] = g
        color[:,0,2] = b
        color[:,1,2] = b
        color[:,2,2] = b
        color[:,3,2] = b
        
        self.glWidget.setQuadData(vertex, color)


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        self.lastPos = QtCore.QPoint()
        
        self.n = 0

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
