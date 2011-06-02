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

from numpy import arange, zeros, ones, log10, ones, hstack, array
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
        self.x1 = array([])
        self.x2 = array([])
        self.y = array([])

        self.verticalScaleEngine = Qwt.QwtLinearScaleEngine()

        self.verticalScale = Qwt.QwtScaleWidget(self)
        self.verticalScale.setTitle("PSD (dB)")
        self.verticalScale.setScaleDiv(self.verticalScaleEngine.transformation(),
                                  self.verticalScaleEngine.divideScale(self.ymin, self.ymax, 8, 5))
        self.verticalScale.setMargin(2)

        self.logx = False
        self.horizontalScaleEngine = Qwt.QwtLinearScaleEngine()

        self.horizontalScale = Qwt.QwtScaleWidget(self)
        self.horizontalScale.setTitle("Frequency (Hz)")
        self.horizontalScale.setScaleDiv(self.horizontalScaleEngine.transformation(),
                                  self.horizontalScaleEngine.divideScale(self.xmin, self.xmax, 8, 5))
        self.horizontalScale.setAlignment(Qwt.QwtScaleDraw.BottomScale)
        self.horizontalScale.setMargin(2)
        #self.horizontalScale.setBorderDist(0,0)
        self.horizontalScale.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)

        #left = self.horizontalScale.getBorderDistHint()[0]
        #right = self.horizontalScale.getBorderDistHint()[1]
        #top = self.verticalScale.getBorderDistHint()[0]
        #bottom = self.verticalScale.getBorderDistHint()[1]

        plotLayout = QtGui.QGridLayout()
        plotLayout.setSpacing(0)
        #plotLayout.addWidget(self.verticalScale, 0, 0, 3, 1)
        plotLayout.addWidget(self.verticalScale, 0, 0)
        #plotLayout.addWidget(self.glWidget, 1, 2)
        plotLayout.addWidget(self.glWidget, 0, 1)
        #plotLayout.addWidget(self.horizontalScale, 3, 1, 1, 3)
        plotLayout.addWidget(self.horizontalScale, 1, 1)
        #plotLayout.setRowMinimumHeight(0, top)
        #plotLayout.setRowMinimumHeight(2, bottom-1)
        #plotLayout.setColumnMinimumWidth(1, left)
        #plotLayout.setColumnMinimumWidth(3, right)
        
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
        
    def xtransform(self, x):
        verticalDists = self.verticalScale.getBorderDistHint()
        horizontalDists = self.horizontalScale.getBorderDistHint()
        self.topDist = verticalDists[0]
        self.bottomDist = verticalDists[1]
        self.leftDist = horizontalDists[0]
        self.rightDist = horizontalDists[1]
        
        if self.logx:
            return (log10(x/self.xmin))*(self.glWidget.width() - self.leftDist - self.rightDist)/(log10(self.xmax/self.xmin)) + self.leftDist
        else:
            return (x - self.xmin)*(self.glWidget.width() - self.leftDist - self.rightDist)/(self.xmax - self.xmin) + self.leftDist

    def ytransform(self, y):
        return (y - self.ymin)*(self.glWidget.height() - self.topDist - self.bottomDist)/(self.ymax - self.ymin) + self.bottomDist - 1
    
    def setdata(self, x, y):        
        x1 = zeros(x.shape)
        x2 = zeros(x.shape)
        x1[0] = 1e-10
        x1[1:] = (x[1:] + x[:-1])/2.
        x2[:-1] = x1[1:]
        x2[-1] = 22050.
        
        # save data for resizing
        self.x1 = x1
        self.x2 = x2
        self.y = y

        self.compute_peaks(y)
        
        self.draw()
        
        # TODO :
        # - picker : special mouse cursor, H anc V rulers, text (QPainter job ?)
        # - pixel mean when band size < pixel size (mean != banding, on purpose)
        # - optimize if further needed, but last point should be more than enough !

    def draw(self):
        transformed_x1 = self.xtransform(self.x1)
        transformed_x2 = self.xtransform(self.x2)
        transformed_y = self.ytransform(self.y)
        transformed_peak = self.ytransform(self.peak)
        
        Ones = ones(self.x1.shape)
        
        x1_with_peaks = hstack((transformed_x1, transformed_x1))
        x2_with_peaks = hstack((transformed_x2, transformed_x2))
        y_with_peaks = hstack((transformed_peak, transformed_y))
        r_with_peaks = hstack((1.*Ones, 0.*Ones))
        g_with_peaks = hstack((1. - self.peak_int, 0.5*Ones))
        b_with_peaks = hstack((1. - self.peak_int, 0.*Ones))
        
        self.setQuadData(x1_with_peaks, y_with_peaks - self.glWidget.height(), x2_with_peaks - x1_with_peaks, self.glWidget.height(), r_with_peaks, g_with_peaks, b_with_peaks)

    # redraw when the widget is resized to update coordinates transformations
    def resizeEvent(self, event):
        self.draw()
        
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
        xMajorTick = self.horizontalScaleEngine.divideScale(self.xmin, self.xmax, 8, 5).ticks(2)
        xMinorTick = self.horizontalScaleEngine.divideScale(self.xmin, self.xmax, 8, 5).ticks(0)
        yMajorTick = self.verticalScaleEngine.divideScale(self.ymin, self.ymax, 8, 5).ticks(2)
        yMinorTick = self.verticalScaleEngine.divideScale(self.ymin, self.ymax, 8, 5).ticks(0)        
        
        self.glWidget.setGrid(self.xtransform(array(xMajorTick)),
                              self.xtransform(array(xMinorTick)),
                              self.ytransform(array(yMajorTick)),
                              self.ytransform(array(yMinorTick))
                              )
        
        # draw the grid here
        #vertex[0,0,0] = 
        
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
        
        self.xMajorTick = array([])
        self.xMinorTick = array([])
        self.yMajorTick = array([])
        self.yMinorTick = array([])

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def initializeGL(self):
        GL.glShadeModel(GL.GL_SMOOTH) # for gradient rendering
        #GL.glDepthFunc(GL.GL_LESS) # The Type Of Depth Test To Do
        GL.glDisable(GL.GL_DEPTH_TEST) # we do 2D, we need no depth test !
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

    def setGrid(self, xMajorTick, xMinorTick, yMajorTick, yMinorTick):
        self.xMajorTick = xMajorTick
        self.xMinorTick = xMinorTick
        self.yMajorTick = yMajorTick
        self.yMinorTick = yMinorTick

    def paintGL(self):
        # Reset The View
        GL.glLoadIdentity()
        
        GL.glClearColor(1, 1, 1, 0)
        # Clear The Screen And The Depth Buffer
        GL.glClear(GL.GL_COLOR_BUFFER_BIT) # | GL.GL_DEPTH_BUFFER_BIT)
        
        w = self.width()
        h = self.height()
        GL.glOrtho(0, w, 0, h, 0, 1)   
        # Displacement trick for exact pixelization
        GL.glTranslatef(0.375, 0.375, 0)
        
        self.drawBackground()
        
        self.drawGrid()
        
        #GL.glDisable(GL.GL_LIGHTING)
        GL.glDrawArrays(GL.GL_QUADS, 0, 4*self.n)
        #GL.glEnable(GL.GL_LIGHTING)
        
        self.drawBorder()

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return
        
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()

    def drawBackground(self):
        w = self.width()
        h = self.height()
        GL.glBegin(GL.GL_QUADS)
        GL.glColor3f(0.85, 0.85, 0.85)
        GL.glVertex2d(0, h)
        GL.glVertex2d(w, h)
        GL.glColor3f(1, 1, 1)
        GL.glVertex2d(w, 0)
        GL.glVertex2d(0, 0)
        GL.glEnd()

    def drawGrid(self):
        w = self.width()
        h = self.height()
        
        self.qglColor(QtGui.QColor(Qt.Qt.gray))
        for x in self.xMajorTick:        
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(x, 0)
            GL.glVertex2f(x, h)
            GL.glEnd()
        
        self.qglColor(QtGui.QColor(Qt.Qt.lightGray))
        for x in self.xMinorTick:        
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(x, 0)
            GL.glVertex2f(x, h)
            GL.glEnd()
            
        self.qglColor(QtGui.QColor(Qt.Qt.gray))
        for y in self.yMajorTick:        
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(0, y)
            GL.glVertex2f(w, y)
            GL.glEnd()
        
        #GL.glColor3f(0.5, 0.5, 0.5)
        #for y in self.yMinorTick:        
        #    GL.glBegin(GL.GL_LINES)
        #    GL.glVertex2f(0, y)
        #    GL.glVertex2f(w, y)
        #    GL.glEnd() 

    def drawBorder(self):
        w = self.width()
        h = self.height()
        self.qglColor(QtGui.QColor(Qt.Qt.gray))
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glVertex2f(0, 0)
        GL.glVertex2f(0, h-1)
        GL.glVertex2f(w, h-1)
        GL.glVertex2f(w, 0)
        GL.glEnd()

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
