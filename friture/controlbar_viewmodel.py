from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot  # type: ignore

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

    @pyqtSlot()  # type: ignore
    def triggerSettingsClicked(self):
        self.settingsClicked.emit()

    @pyqtSlot()  # type: ignore
    def triggerMovePreviousClicked(self):
        self.movePreviousClicked.emit()

    @pyqtSlot()  # type: ignore
    def triggerMoveNextClicked(self):
        self.moveNextClicked.emit()

    @pyqtSlot()  # type: ignore
    def triggerCloseClicked(self):
        self.closeClicked.emit()
