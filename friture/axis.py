from PyQt5 import QtCore
from PyQt5.QtCore import pyqtProperty, pyqtSlot

class Axis(QtCore.QObject):
    name_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._name = "Axis Name"
        self._formatter = lambda x: str(x)

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
