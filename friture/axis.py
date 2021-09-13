from PyQt5 import QtCore
from PyQt5.QtCore import pyqtProperty, pyqtSlot

from friture.plotting.coordinateTransform import CoordinateTransform
from friture.plotting.scaleDivision import ScaleDivision

class Axis(QtCore.QObject):
    name_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._name = "Axis Name"
        self._formatter = lambda x: str(x)
        self._scale_division = ScaleDivision(-1., 1.)
        self._coordinate_transform = CoordinateTransform(-1, 1, 1., 0, 0)

    @pyqtProperty(str, notify=name_changed)
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        if self._name != name:
            self._name = name
            self.name_changed.emit(name)
    
    def setTrackerFormatter(self, formatter):
        if self._formatter != formatter:
            self._formatter = formatter
    
    @pyqtSlot(float, result=str)
    def formatTracker(self, value):
        return self._formatter(value)

    def setRange(self, scale_min, scale_max):
        self._scale_division.setRange(scale_min, scale_max)
        self._coordinate_transform.setRange(scale_min, scale_max)
    
    @pyqtProperty(ScaleDivision, constant=True)
    def scale_division(self):
        return self._scale_division
    
    @pyqtProperty(CoordinateTransform, constant=True)
    def coordinate_transform(self):
        return self._coordinate_transform
