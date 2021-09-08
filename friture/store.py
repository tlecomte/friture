from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtProperty
from PyQt5.QtQml import QQmlListProperty

__storeInstance = None

def GetStore():
    global __storeInstance
    if __storeInstance is None:
        __storeInstance = Store()
    return __storeInstance

class Store(QtCore.QObject):
    dock_states_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dock_states = []
    
    @pyqtProperty(QQmlListProperty, notify=dock_states_changed)
    def dock_states(self):
        return QQmlListProperty(QObject, self, self._dock_states)
