from PyQt5.QtWidgets import QApplication
from PyQt5.QtQuick import QQuickView
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QUrl
import sys
import os

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

app = QApplication(sys.argv)
pal = QPalette()
pal.setColor(QPalette.Window, QColor('blue'))
pal.setColor(QPalette.WindowText, QColor('white'))
app.setPalette(pal)

view = QQuickView()
view.setSource(QUrl.fromLocalFile('test_page.qml'))
print("View rendered.")
