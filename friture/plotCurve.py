import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtProperty # type: ignore
from PyQt5.QtGui import QColor
from PyQt5.QtQuick import QQuickItem, QSGGeometryNode, QSGGeometry, QSGFlatColorMaterial, QSGNode # type: ignore

from friture.curve import Curve

class PlotCurve(QQuickItem):
    colorChanged = pyqtSignal()
    curveChanged = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setFlag(QQuickItem.ItemHasContents, True)

        self._x_array = np.array([0])
        self._y_array = np.array([0])

        self._color = QColor("black")
        self._curve = Curve()

    @pyqtProperty(QColor, notify=colorChanged)
    def color(self):
        return self._color

    @color.setter # type: ignore
    def color(self, color):
        if color != self._color:
            self._color = color
            self.update()
            self.colorChanged.emit()

    @pyqtProperty(Curve, notify=curveChanged)
    def curve(self):
        return self._curve

    @curve.setter # type: ignore
    def curve(self, curve):
        if curve != self._curve:
            self._curve = curve
            if self._curve is not None:
                self._curve.data_changed.connect(self.update)

            self.update()
            self.curveChanged.emit()

    def updatePaintNode(self, paint_node, update_data):
        if paint_node is None:
            paint_node = QSGGeometryNode()

            geometry = QSGGeometry(QSGGeometry.defaultAttributes_Point2D(), self.curve.x_array().size)
            geometry.setLineWidth(2)
            geometry.setDrawingMode(QSGGeometry.GL_LINE_STRIP)
            paint_node.setGeometry(geometry)
            paint_node.setFlag(QSGNode.OwnsGeometry)

            material = QSGFlatColorMaterial()
            material.setColor(self._color)
            paint_node.setMaterial(material)
            paint_node.setFlag(QSGNode.OwnsMaterial)
            paint_node.markDirty(QSGNode.DirtyMaterial)

        else:
            geometry = paint_node.geometry()
            geometry.allocate(self.curve.x_array().size) # geometry will be marked as dirty below

            material = paint_node.material()
            if material.color() != self._color:
                material.setColor(self._color)
                paint_node.markDirty(QSGNode.DirtyMaterial)

        size = self.curve.x_array().size

        # ideally we would use geometry.vertexDataAsPoint2D
        # but there is a bug with the returned sip.array
        # whose total size is not interpreted correctly
        # `memoryview(geometry.vertexDataAsPoint2D()).nbytes` does not take itemsize into account
        vertices = geometry.vertexData()
        vertices.setsize(2 * np.dtype(np.float32).itemsize * size)

        polygon_array = np.frombuffer(vertices, dtype=np.float32)
        polygon_array[: (size - 1) * 2 + 1 : 2] = np.array(self.curve.x_array() * self.width(), dtype=np.float32, copy=False)
        polygon_array[1 : (size - 1) * 2 + 2 : 2] = np.array(self.curve.y_array() * self.height(), dtype=np.float32, copy=False)

        paint_node.markDirty(QSGNode.DirtyGeometry)

        return paint_node