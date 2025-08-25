from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtProperty
from PyQt5.QtQml import QQmlListProperty # type: ignore

__storeInstance = None

def GetStore():
    global __storeInstance
    if __storeInstance is None:
        __storeInstance = Store()
    return __storeInstance

class Store(QtCore.QObject):
    dock_states_changed = QtCore.pyqtSignal()
    transparency_changed = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dock_states = []
        self._transparency_enabled = True  # Default to enabled

    @pyqtProperty(QQmlListProperty, notify=dock_states_changed) # type: ignore
    def dock_states(self):
        return QQmlListProperty(QObject, self, self._dock_states)

    @pyqtProperty(bool, notify=transparency_changed) # type: ignore
    def transparency_enabled(self):
        return self._transparency_enabled

    @transparency_enabled.setter # type: ignore
    def transparency_enabled(self, enabled):
        if self._transparency_enabled != enabled:
            self._transparency_enabled = enabled
            self.transparency_changed.emit(enabled)
