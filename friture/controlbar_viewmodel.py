from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty

class ControlBarViewModel(QObject):
    indexChanged = pyqtSignal(int)
    settingsClicked = pyqtSignal()
    movePreviousClicked = pyqtSignal()
    moveNextClicked = pyqtSignal()
    closeClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._currentIndex = 0

    def getCurrentIndex(self):
        return self._currentIndex

    def setCurrentIndex(self, index):
        if self._currentIndex != index:
            self._currentIndex = index
            self.indexChanged.emit(index)

    currentIndex = pyqtProperty(int, fget=getCurrentIndex, fset=setCurrentIndex, notify=indexChanged)

    def onSettingsClicked(self):
        self.settingsClicked.emit()

    def onMovePreviousClicked(self):
        self.movePreviousClicked.emit()

    def onMoveNextClicked(self):
        self.moveNextClicked.emit()

    def onCloseClicked(self):
        self.closeClicked.emit()
