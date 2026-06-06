from PyQt5.QtWidgets import QApplication
from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QUrl
import sys
import os

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

app = QApplication(sys.argv)
view = QQuickView()
view.setSource(QUrl.fromLocalFile('test_inherit.qml'))
print("Rendered.")
