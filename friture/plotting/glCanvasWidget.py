import sys
import logging
from ctypes import sizeof, c_float, c_void_p, c_uint

from PyQt5 import QtCore, QtGui, Qt, QtWidgets
import numpy as np
import pyrr
from OpenGL import GL
from OpenGL.arrays import vbo

def compileProgram(*shaders):
    """Copied from the PyOpenGL codebase, as suggested in the PyOpenGL doc.
    Does not call program.check_validate() because that fails on macos
    because the framebuffer is not ready at initialization time"""
    program = GL.glCreateProgram()
    for shader in shaders:
        GL.shaders.glAttachShader(program, shader)
    program = GL.shaders.ShaderProgram(program)
    GL.glLinkProgram(program)
    program.check_linked()
    for shader in shaders:
        GL.glDeleteShader(shader)
    return program


class GlCanvasWidget(QtWidgets.QOpenGLWidget):

    resized = QtCore.pyqtSignal(int, int)

    def __init__(self, parent, verticalScaleTransform, horizontalScaleTransform):
        super(GlCanvasWidget, self).__init__(parent)

        self.logger = logging.getLogger(__name__)

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

        self.gridNeedsUpdating = True
        self.backgroundNeedsUpdating = True
        self.matrixNotSet = True

        self.horizontalScaleTransform = horizontalScaleTransform
        self.verticalScaleTransform = verticalScaleTransform

        self.trackerFormatter = lambda x, y: "x=%d, y=%d" % (x, y)

        self.anyOpaqueItem = False

        self.paused = False

        self.quad_shader = None
        self.background_vbo = None
        self.border_vbo = None
        self.ruler_vbo = None
        self.grid_vbo = None
        self.data_vbo = None
        self.vao = None

        # True for OpenGL Core profile, False for Compatibility profile
        self.is_core = None

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
            item.glDraw(self.horizontalScaleTransform, self.verticalScaleTransform, self.rect(), self.data_vbo, self.quad_shader)

    def sizeHint(self):
        return QtCore.QSize(50, 50)

    def logOpenGLFormat(self, format):
        try:
            profile = format.profile()
            if profile == QtGui.QSurfaceFormat.NoProfile:
                profile_name = "No profile"
            elif profile == QtGui.QSurfaceFormat.CoreProfile:
                profile_name = "Core profile"
            elif profile == QtGui.QSurfaceFormat.CompatibilityProfile:
                profile_name = "Compatibility profile"
            else:
                profile_name = "Unknown profile"

            renderableType = format.renderableType()
            if renderableType == QtGui.QSurfaceFormat.DefaultRenderableType:
                renderableType_name = "Unspecified rendering"
            elif renderableType == QtGui.QSurfaceFormat.OpenGL:
                renderableType_name = "Desktop OpenGL rendering"
            elif renderableType == QtGui.QSurfaceFormat.OpenGLES:
                renderableType_name = "OpenGL ES 2.0 rendering"
            elif renderableType == QtGui.QSurfaceFormat.OpenVG:
                renderableType_name = "OpenVG rendering"
            else:
                renderableType_name = "Unknown rendering"

            self.logger.info(
                "OpenGL format: version %d.%d, %s, %s",
                format.majorVersion(),
                format.minorVersion(),
                profile_name,
                renderableType_name)

            self.logger.info(
                "%s, %s, Version: %s, Shaders: %s, Extensions: %s",
                self.tryGlGetString(GL.GL_VENDOR),
                self.tryGlGetString(GL.GL_RENDERER),
                self.tryGlGetString(GL.GL_VERSION),
                self.tryGlGetString(GL.GL_SHADING_LANGUAGE_VERSION),
                self.tryGlGetIntegerv(GL.GL_NUM_EXTENSIONS)
            )
        except Exception:
            self.logger.exception("Failed to log the OpenGL info")

    def tryGlGetString(self, enum):
        try:
            return GL.glGetString(enum).decode("utf-8")
        except Exception:
            self.logger.exception("glGetString failed")
            return "unknown"

    def tryGlGetIntegerv(self, enum):
        try:
            return GL.glGetIntegerv(enum)
        except Exception:
            self.logger.exception("glGetIntegerv failed")
            return "unknown"

    def build_model_view_projection_matrix(self, translation, rotation, scale):
        translation_matrix = np.transpose(pyrr.matrix44.create_from_translation(translation))
        rotation_matrix = np.transpose(pyrr.matrix44.create_from_y_rotation(rotation))
        scale_matrix = np.transpose(pyrr.matrix44.create_from_scale(scale))

        model_matrix = np.matmul(np.matmul(translation_matrix, rotation_matrix), scale_matrix)
        view_matrix = np.transpose(pyrr.matrix44.create_identity())
        projection_matrix = np.transpose(pyrr.matrix44.create_orthogonal_projection_matrix(0, self.width(), 0, self.height(), 0, 1))
        m = np.matmul(np.matmul(projection_matrix, view_matrix), model_matrix)

        return np.transpose(m)

    def initializeGL(self):
        openGL_format = self.format()

        self.is_core = openGL_format.profile() == QtGui.QSurfaceFormat.CoreProfile

        self.logOpenGLFormat(openGL_format)
        self.clearErrors()

        legacy_vertex_shader_source = """
            #version 110

            // input
            attribute vec3 in_color;
            uniform mat4 mvp;

            // output
            varying vec3 out_color;

            void main()
            {
                gl_Position = mvp * gl_Vertex;
                out_color = in_color;
            }"""

        core_vertex_shader_source = """
            #version 150 core

            // input
            in vec3 in_position;
            in vec3 in_color;
            uniform mat4 mvp;

            // output
            out vec3 out_color;

            void main()
            {
                gl_Position = mvp * vec4(in_position, 1.0);
                out_color = in_color;
            }"""

        vertex_shader_source = core_vertex_shader_source if self.is_core else legacy_vertex_shader_source
        quad_vertex_shader = GL.shaders.compileShader(vertex_shader_source, GL.GL_VERTEX_SHADER)

        legacy_fragment_shader_source = """
            #version 110

            // input
            varying vec3 out_color;

            void main()
            {
                gl_FragColor = vec4(out_color, 1.0);
            }"""

        core_fragment_shader_source = """
            #version 150 core

            // input
            in vec3 out_color;

            // output
            out vec4 frag_color;

            void main()
            {
                frag_color = vec4(out_color, 1.0);
            }"""

        fragment_shader_source = core_fragment_shader_source if self.is_core else legacy_fragment_shader_source
        quad_fragment_shader = GL.shaders.compileShader(fragment_shader_source, GL.GL_FRAGMENT_SHADER)

        if self.is_core:
            # on OpenGL 3 core, create a vertex array object (on non-core, there is one default VAO)
            self.vao = GL.glGenVertexArrays(1)
            # VAO needs to be bound before the program can be compiled
            GL.glBindVertexArray(self.vao)

        self.quad_shader = compileProgram(quad_vertex_shader, quad_fragment_shader)

        vertices = np.array(
            [[0, 100, 0],
             [100, 100, 0],
             [100, 0, 0],
             [200, 200, 0],
             [200, 400, 0],
             [400, 400, 0],
             [400, 400, 0],
             [200, 200, 0],
             [400, 200, 0]], 'f')

        self.background_vbo = vbo.VBO(vertices)
        self.border_vbo = vbo.VBO(vertices)
        self.ruler_vbo = vbo.VBO(vertices)
        self.grid_vbo = vbo.VBO(vertices)
        self.data_vbo = vbo.VBO(vertices)

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
        w = self.width()
        h = self.height()

        # given the usual aspect ratio of the canvas, the vertical minor ticks would make it look crowded
        num_lines = len(self.xMajorTick) + len(self.xMinorTick) + len(self.yMajorTick)  # + len(self.yMinorTick)
        num_lines *= 2

        self.grid_data = np.zeros((num_lines, 6), dtype=np.float32)

        i = 0

        color = QtGui.QColor(Qt.Qt.gray)
        for x in self.xMajorTick:
            self.grid_data[i, :] = [x, 0, 0, color.redF(), color.greenF(), color.blueF()]
            self.grid_data[i+1, :] = [x, h, 0, color.redF(), color.greenF(), color.blueF()]
            i += 2

        color = QtGui.QColor(Qt.Qt.lightGray)
        for x in self.xMinorTick:
            self.grid_data[i, :] = [x, 0, 0, color.redF(), color.greenF(), color.blueF()]
            self.grid_data[i+1, :] = [x, h, 0, color.redF(), color.greenF(), color.blueF()]
            i += 2

        color = QtGui.QColor(Qt.Qt.gray)
        for y in self.yMajorTick:
            self.grid_data[i, :] = [0, y, 0, color.redF(), color.greenF(), color.blueF()]
            self.grid_data[i+1, :] = [w, y, 0, color.redF(), color.greenF(), color.blueF()]
            i += 2

        # given the usual aspect ratio of the canvas, the vertical minor ticks would make it look crowded
        # color = QtGui.QColor(Qt.Qt.lightGray)
        # for y in self.yMinorTick:
        #     self.grid_data[i,   :] = [0, y, 0, color.redF(), color.greenF(), color.blueF()]
        #     self.grid_data[i+1, :] = [w, y, 0, color.redF(), color.greenF(), color.blueF()]
        #     i += 2

        self.grid_vbo.set_array(self.grid_data)

        self.gridNeedsUpdating = False

    def updateBackground(self):
        w = self.width()
        h = self.height()
        self.background_data = np.array(
            [[0, h,   0, 0.85, 0.85, 0.85],
             [w, h, 0, 0.85, 0.85, 0.85],
             [0, h/2, 0, 1.0,  1.0,  1.0],
             [w, h / 2, 0, 1.0, 1.0, 1.0]],
            dtype=np.float32)

        self.background_vbo.set_array(self.background_data)

        # also update the border
        color = QtGui.QColor(Qt.Qt.gray)
        self.border_data = np.array(
            [[0,   0,   0, color.redF(), color.greenF(), color.blueF()],
             [0,   h-1, 0, color.redF(), color.greenF(), color.blueF()],
             [w-1, h-1, 0, color.redF(), color.greenF(), color.blueF()],
             [w-1, 0,   0, color.redF(), color.greenF(), color.blueF()],
             [0,   0,   0, color.redF(), color.greenF(), color.blueF()]],
            dtype=np.float32)

        self.border_vbo.set_array(self.border_data)

        self.backgroundNeedsUpdating = False

    def clearErrors(self):
        # try to clear the errors that are produced outside of this code - for example Qt errors
        error = GL.glGetError()
        while error != GL.GL_NO_ERROR:
            self.logger.error("Clearing an OpenGL error that occured outside of Friture code: %s", error)
            error = GL.glGetError()

    def paintGL(self):
        if self.quad_shader is None:
            return  # not yet initiliazed

        self.clearErrors()

        # Clear The Screen And The Depth Buffer
        GL.glClearColor(1, 1, 1, 0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)  # | GL.GL_DEPTH_BUFFER_BIT)

        GL.glUseProgram(self.quad_shader)

        if self.is_core:
            # on OpenGL 3 core, create and bind a vertex array object (on non-core, there is one default VAO)
            GL.glBindVertexArray(self.vao)

        try:
            self.setupViewport(self.width(), self.height())

            self.drawBackground()
            self.drawGrid()
            self.drawGlData()
            self.drawRuler()
            self.drawBorder()
        finally:
            if self.is_core:
                GL.glBindVertexArray(0)

            GL.glUseProgram(0)

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
        self.backgroundNeedsUpdating = True
        self.matrixNotSet = True

        # give the opportunity to the scales to adapt
        self.resized.emit(self.width(), self.height())

    def setupViewport(self, width, height):
        if self.matrixNotSet:
            translation = pyrr.Vector3([0.375, 0.375, 0])
            rotation = 0.0
            scale = pyrr.Vector3([1.0, 1.0, 1.0])
            mvp = self.build_model_view_projection_matrix(translation, rotation, scale)

            mvp_uniform_location = GL.glGetUniformLocation(self.quad_shader, "mvp")
            GL.glUniformMatrix4fv(mvp_uniform_location, 1, GL.GL_FALSE, mvp)

            self.matrixNotSet = False

        GL.glDisable(GL.GL_DEPTH_TEST)  # we do 2D, we need no depth test !

    def drawBackground(self):
        if self.anyOpaqueItem:
            return

        if self.backgroundNeedsUpdating:
            self.updateBackground()

        self.background_vbo.bind()
        try:
            GL.glEnableVertexAttribArray(0)
            GL.glEnableVertexAttribArray(1)
            stride = self.background_data.shape[1]*sizeof(c_float)
            vertex_offset = c_void_p(0 * sizeof(c_float))
            color_offset = c_void_p(3 * sizeof(c_float))
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, vertex_offset)
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, color_offset)
            GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, self.background_data.shape[0])
            GL.glDisableVertexAttribArray(0)
            GL.glDisableVertexAttribArray(1)
        finally:
            self.background_vbo.unbind()

    def drawGrid(self):
        if self.anyOpaqueItem:
            return

        if self.gridNeedsUpdating:
            self.updateGrid()

        self.grid_vbo.bind()
        try:
            GL.glEnableVertexAttribArray(0)
            GL.glEnableVertexAttribArray(1)
            stride = self.grid_data.shape[1]*sizeof(c_float)
            vertex_offset = c_void_p(0 * sizeof(c_float))
            color_offset = c_void_p(3 * sizeof(c_float))
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, vertex_offset)
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, color_offset)
            GL.glDrawArrays(GL.GL_LINES, 0, self.grid_data.shape[0])
            GL.glDisableVertexAttribArray(0)
            GL.glDisableVertexAttribArray(1)
        finally:
            self.grid_vbo.unbind()

    def drawBorder(self):
        self.border_vbo.bind()
        try:
            GL.glEnableVertexAttribArray(0)
            GL.glEnableVertexAttribArray(1)
            stride = self.border_data.shape[1]*sizeof(c_float)
            vertex_offset = c_void_p(0 * sizeof(c_float))
            color_offset = c_void_p(3 * sizeof(c_float))
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, vertex_offset)
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, color_offset)
            GL.glDrawArrays(GL.GL_LINE_STRIP, 0, self.border_data.shape[0])
            GL.glDisableVertexAttribArray(0)
            GL.glDisableVertexAttribArray(1)
        finally:
            self.border_vbo.unbind()

    def drawRuler(self):
        if self.ruler:
            w = self.width()
            h = self.height()
            color = QtGui.QColor(Qt.Qt.black)
            self.ruler_data = np.array(
                [[self.mousex, 0,               0, color.redF(), color.greenF(), color.blueF()],
                 [self.mousex, h,               0, color.redF(), color.greenF(), color.blueF()],
                 [0,           h - self.mousey, 0, color.redF(), color.greenF(), color.blueF()],
                 [w,           h - self.mousey, 0, color.redF(), color.greenF(), color.blueF()]],
                dtype=np.float32)

            self.ruler_vbo.set_array(self.ruler_data)

            self.ruler_vbo.bind()
            try:
                GL.glEnableVertexAttribArray(0)
                GL.glEnableVertexAttribArray(1)
                stride = self.ruler_data.shape[1]*sizeof(c_float)
                vertex_offset = c_void_p(0 * sizeof(c_float))
                color_offset = c_void_p(3 * sizeof(c_float))
                GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, vertex_offset)
                GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, color_offset)
                GL.glDrawArrays(GL.GL_LINES, 0, self.ruler_data.shape[0])
                GL.glDisableVertexAttribArray(0)
                GL.glDisableVertexAttribArray(1)
            finally:
                self.ruler_vbo.unbind()

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
