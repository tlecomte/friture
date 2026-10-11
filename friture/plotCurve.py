import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty # type: ignore  # type: ignore
from PyQt6.QtGui import QColor
from PyQt6.QtQuick import QQuickItem, QSGGeometryNode, QSGGeometry, QSGFlatColorMaterial, QSGNode # type: ignore

from friture.curve import Curve

class PlotCurve(QQuickItem):
    colorChanged = pyqtSignal()
    curveChanged = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setFlag(QQuickItem.Flag.ItemHasContents, True)

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

    @pyqtProperty(QObject, notify=curveChanged)
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
        # Non-finite samples are gaps. A GL line strip cannot have gaps (NaN
        # vertices render as lines to the plot edge), so draw independent
        # segments between consecutive finite points instead.
        x = np.asarray(self.curve.x_array() * self.width(), dtype=np.float32)
        y = np.asarray(self.curve.y_array() * self.height(), dtype=np.float32)
        valid = np.isfinite(x) & np.isfinite(y)
        pair_ok = valid[:-1] & valid[1:]
        idx = np.flatnonzero(pair_ok)
        size = 2 * idx.size

        if paint_node is None:
            paint_node = QSGGeometryNode()

            geometry = QSGGeometry(QSGGeometry.defaultAttributes_Point2D(), size)
            geometry.setLineWidth(2)
            geometry.setDrawingMode(QSGGeometry.DrawingMode.DrawLines)
            paint_node.setGeometry(geometry)
            paint_node.setFlag(QSGNode.Flag.OwnsGeometry)

            material = QSGFlatColorMaterial()
            material.setColor(self._color)
            paint_node.setMaterial(material)
            paint_node.setFlag(QSGNode.Flag.OwnsMaterial)
            paint_node.markDirty(QSGNode.DirtyStateBit.DirtyMaterial)

        else:
            geometry = paint_node.geometry()
            geometry.allocate(size) # geometry will be marked as dirty below

            material = paint_node.material()
            if material.color() != self._color:
                material.setColor(self._color)
                paint_node.markDirty(QSGNode.DirtyStateBit.DirtyMaterial)

        if size > 0:
            # ideally we would use geometry.vertexDataAsPoint2D
            # but there is a bug with the returned sip.array
            # whose total size is not interpreted correctly
            # `memoryview(geometry.vertexDataAsPoint2D()).nbytes` does not take itemsize into account
            vertices = geometry.vertexData()
            vertices.setsize(2 * np.dtype(np.float32).itemsize * size)

            polygon_array = np.frombuffer(vertices, dtype=np.float32).reshape(-1, 2, 2)  # segment, endpoint, xy
            polygon_array[:, 0, 0] = x[idx]
            polygon_array[:, 0, 1] = y[idx]
            polygon_array[:, 1, 0] = x[idx + 1]
            polygon_array[:, 1, 1] = y[idx + 1]

        paint_node.markDirty(QSGNode.DirtyStateBit.DirtyGeometry)

        return paint_node
