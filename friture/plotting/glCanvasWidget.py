import sys

from PyQt5 import QtCore, QtGui, Qt, QtWidgets
import numpy as np

try:
    from OpenGL import GL
except ImportError:
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None, "OpenGL hellogl",
                                   "PyOpenGL must be installed to run this example.")
    sys.exit(1)


class GlCanvasWidget(QtWidgets.QOpenGLWidget):

    resized = QtCore.pyqtSignal(int, int)

    def __init__(self, parent, verticalScaleTransform, horizontalScaleTransform):
        super(GlCanvasWidget, self).__init__(parent)

        self.lastPos = QtCore.QPoint()

        self.xMajorTick = np.array([])
        self.xMinorTick = np.array([])
        self.yMajorTick = np.array([])
        self.yMinorTick = np.array([])

        self.ruler = False
        self.mousex = 0
        self.mousey = 0

        self.showFreqLabel = False
        self.xmax = 0
        self.fmax = 0.

        # use a cross cursor to easily select a point on the graph
        self.setCursor(Qt.Qt.CrossCursor)

        # set proper size policy for this widget
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))

        self.attachedItems = []

        self.gridList = None
        self.gridNeedsUpdating = True

        self.horizontalScaleTransform = horizontalScaleTransform
        self.verticalScaleTransform = verticalScaleTransform

        self.trackerFormatter = lambda x, y: "x=%d, y=%d" % (x, y)

        self.anyOpaqueItem = False

        self.paused = False

    def setTrackerFormatter(self, formatter):
        self.trackerFormatter = formatter

    def attach(self, item):
        self.attachedItems.append(item)
        self.reviewOpaqueItems()

    def detach(self, item):
        self.attachedItems.remove(item)
        self.reviewOpaqueItems()

    def detachAll(self):
        self.attachedItems.clear()
        self.reviewOpaqueItems()

    def pause(self):
        self.paused = True

    def restart(self):
        self.paused = False

    def reviewOpaqueItems(self):
        self.anyOpaqueItem = False
        for item in self.attachedItems:
            try:
                if item.isOpaque():
                    self.anyOpaqueItem = True
            except:
                # do nothing
                continue

    def drawGlData(self):
        for item in self.attachedItems:
            item.glDraw(self.horizontalScaleTransform, self.verticalScaleTransform, self.rect())

    def sizeHint(self):
        return QtCore.QSize(50, 50)

    def initializeGL(self):
        return

    def setfmax(self, fmax):
        self.fmax = fmax

    def setShowFreqLabel(self, showFreqLabel):
        self.showFreqLabel = showFreqLabel
        # ask for update so the the label is actually erased or painted
        self.update()

    def setGrid(self, xMajorTick, xMinorTick, yMajorTick, yMinorTick):
        self.xMajorTick = self.horizontalScaleTransform.toScreen(xMajorTick)
        self.xMinorTick = self.horizontalScaleTransform.toScreen(xMinorTick)
        self.yMajorTick = self.verticalScaleTransform.toScreen(yMajorTick)
        self.yMinorTick = self.verticalScaleTransform.toScreen(yMinorTick)

        # trigger a grid update on next paintGL call
        self.gridNeedsUpdating = True

    def updateGrid(self):
        if self.gridList is None or self.gridList == 0:
            return

        w = self.width()
        h = self.height()

        GL.glNewList(self.gridList, GL.GL_COMPILE)

        color = QtGui.QColor(Qt.Qt.gray)
        GL.glColor3f(color.redF(), color.greenF(), color.blueF())
        for x in self.xMajorTick:
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(x, 0)
            GL.glVertex2f(x, h)
            GL.glEnd()

        color = QtGui.QColor(Qt.Qt.lightGray)
        GL.glColor3f(color.redF(), color.greenF(), color.blueF())
        for x in self.xMinorTick:
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(x, 0)
            GL.glVertex2f(x, h)
            GL.glEnd()

        color = QtGui.QColor(Qt.Qt.gray)
        GL.glColor3f(color.redF(), color.greenF(), color.blueF())
        for y in self.yMajorTick:
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(0, y)
            GL.glVertex2f(w, y)
            GL.glEnd()

        # given the usual aspect ratio of the canvas, the vertical minor ticks would make it look crowded
        # GL.glColor3f(0.5, 0.5, 0.5)
        # for y in self.yMinorTick:
        #    GL.glBegin(GL.GL_LINES)
        #    GL.glVertex2f(0, y)
        #    GL.glVertex2f(w, y)
        #    GL.glEnd()

        GL.glEndList()

        self.gridNeedsUpdating = False

    def paintGL(self):
        # try to clear the errors that are produced outside of this code - for example Qt errors
        error = GL.glGetError()
        while error != GL.GL_NO_ERROR:
            print("Clearing an OpenGL error that occured outside of Friture code", error)
            error = GL.glGetError()

        self.setupViewport(self.width(), self.height())

        # Clear The Screen And The Depth Buffer
        GL.glClearColor(1, 1, 1, 0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)  # | GL.GL_DEPTH_BUFFER_BIT)

        self.drawBackground()
        self.drawGrid()
        self.drawGlData()
        self.drawRuler()
        self.drawBorder()

        painter = QtGui.QPainter(self)
        self.drawTrackerText(painter)
        self.drawFreqMaxText(painter)

        painter.end()

        if not self.paused:
            # schedule a repaint !
            self.update()

    def drawFreqMaxText(self, painter):
        if not self.showFreqLabel:
            return

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if self.fmax < 2e2:
            text = "%.1f Hz" % (self.fmax)
        else:
            text = "%d Hz" % (np.rint(self.fmax))

        xmax = self.horizontalScaleTransform.toScreen(self.fmax)
        if xmax == np.inf or xmax == -np.inf:
            xmax = 0
        else:
            xmax = int(xmax)

        # compute tracker bounding rect
        painter.setPen(Qt.Qt.black)
        rect = painter.boundingRect(QtCore.QRect(xmax, 0, 0, 0), Qt.Qt.AlignHCenter, text)

        # avoid crossing the left and top borders
        dx = - min(rect.x() - 2, 0)
        dy = - min(rect.y() - 1, 0)
        rect.translate(dx, dy)

        # avoid crossing the right and bottom borders
        dx = - max(rect.right() - self.width() + 2, 0)
        dy = - max(rect.bottom() - self.height() + 1, 0)
        rect.translate(dx, dy)

        Hmiddle = (rect.left() + rect.right()) / 2
        triangleSize = 4

        # draw a white background
        painter.setPen(Qt.Qt.NoPen)
        painter.setBrush(Qt.Qt.white)
        painter.drawRect(rect)

        # draw a little downward-pointing triangle to indicate the frequency
        # triangle fill
        polygon = QtGui.QPolygon()
        polygon << QtCore.QPoint(Hmiddle - triangleSize, rect.bottom() + 1)
        polygon << QtCore.QPoint(Hmiddle, rect.bottom() + 1 + triangleSize)
        polygon << QtCore.QPoint(Hmiddle + triangleSize, rect.bottom() + 1)
        painter.drawPolygon(polygon)

        # triangle outline
        painter.setPen(Qt.Qt.black)
        painter.drawLine(rect.left(), rect.bottom() + 1, Hmiddle - triangleSize, rect.bottom() + 1)
        painter.drawLine(Hmiddle - triangleSize, rect.bottom() + 1, Hmiddle, rect.bottom() + 1 + triangleSize)
        painter.drawLine(Hmiddle, rect.bottom() + 1 + triangleSize, Hmiddle + triangleSize, rect.bottom() + 1)
        painter.drawLine(Hmiddle + triangleSize, rect.bottom() + 1, rect.right(), rect.bottom() + 1)

        # frequency label
        painter.setPen(Qt.Qt.black)
        painter.drawText(rect, Qt.Qt.AlignLeft, text)

    def drawTrackerText(self, painter):
        if self.ruler:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            x = self.horizontalScaleTransform.toPlot(self.mousex)
            y = self.verticalScaleTransform.toPlot(float(self.height() - self.mousey))
            text = self.trackerFormatter(x, y)

            # compute tracker bounding rect
            painter.setPen(Qt.Qt.black)
            rect = painter.boundingRect(QtCore.QRect(self.mousex, self.mousey, 0, 0), Qt.Qt.AlignLeft, text)

            # small offset so that it does not touch the rulers
            rect.translate(4, -(rect.height() + 4))

            # avoid crossing the top and right borders
            dx = - max(rect.x() + rect.width() - self.width(), 0)
            dy = - min(rect.y(), 0)
            rect.translate(dx, dy)

            # avoid crossing the left and bottom borders
            dx = - min(rect.x(), 0)
            dy = - max(rect.y() + rect.height() - self.height(), 0)
            rect.translate(dx, dy)

            # draw a white background
            painter.setPen(Qt.Qt.NoPen)
            painter.setBrush(Qt.Qt.white)
            painter.drawRect(rect)

            painter.setPen(Qt.Qt.black)
            painter.drawText(rect, Qt.Qt.AlignLeft, text)

    def resizeGL(self, width, height):
        self.gridNeedsUpdating = True

        # give the opportunity to the scales to adapt
        self.resized.emit(self.width(), self.height())

    def setupViewport(self, width, height):
        #GL.glViewport(0, 0, width, height) #redundant with Qt setup, and possibly buggy
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, width, 0, height, 0, 1)
        # Displacement trick for exact pixelization
        GL.glTranslatef(0.375, 0.375, 0)

        GL.glShadeModel(GL.GL_SMOOTH)  # for gradient rendering
        # GL.glDepthFunc(GL.GL_LESS) # The Type Of Depth Test To Do
        GL.glDisable(GL.GL_DEPTH_TEST)  # we do 2D, we need no depth test !
        # GL.glEnable(GL.GL_CULL_FACE)

    def drawBackground(self):
        if self.anyOpaqueItem:
            return

        w = self.width()
        h = self.height()
        GL.glBegin(GL.GL_QUADS)
        GL.glColor3f(0.85, 0.85, 0.85)
        GL.glVertex2d(0, h)
        GL.glVertex2d(w, h)
        GL.glColor3f(1, 1, 1)
        GL.glVertex2d(w, h / 2)
        GL.glVertex2d(0, h / 2)
        GL.glEnd()

    def drawGrid(self):
        if self.anyOpaqueItem:
            return

        if self.gridList is None:
            # display list used for the grid
            self.gridList = GL.glGenLists(1)

            if self.gridList == 0 or self.gridList is None:
                raise RuntimeError("""Unable to generate a new display-list, context may not support display lists""")

        if self.gridNeedsUpdating:
            self.updateGrid()

        GL.glCallList(self.gridList)

    def drawBorder(self):
        w = self.width()
        h = self.height()
        color = QtGui.QColor(Qt.Qt.gray)
        GL.glColor3f(color.redF(), color.greenF(), color.blueF())
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glVertex2f(0, 0)
        GL.glVertex2f(0, h - 1)
        GL.glVertex2f(w - 1, h - 1)
        GL.glVertex2f(w - 1, 0)
        GL.glEnd()

    def drawRuler(self):
        if self.ruler:
            w = self.width()
            h = self.height()
            color = QtGui.QColor(Qt.Qt.black)
            GL.glColor3f(color.redF(), color.greenF(), color.blueF())
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(self.mousex, 0)
            GL.glVertex2f(self.mousex, h)
            GL.glVertex2f(0, h - self.mousey)
            GL.glVertex2f(w, h - self.mousey)
            GL.glEnd()

    def mousePressEvent(self, event):
        self.lastPos = event.pos()
        self.mousex = event.x()
        self.mousey = event.y()
        self.ruler = True
        # ask for update so the the ruler is actually painted
        self.update()

    def mouseReleaseEvent(self, event):
        self.ruler = False
        # ask for update so the the ruler is actually erased
        self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.mousex = event.x()
            self.mousey = event.y()
            self.update()
