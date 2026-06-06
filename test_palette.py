from PyQt5.QtWidgets import QApplication
from PyQt5.QtQuick import QQuickView
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QUrl
import sys

app = QApplication(sys.argv)
pal = QPalette()
pal.setColor(QPalette.Window, QColor('blue'))
pal.setColor(QPalette.WindowText, QColor('white'))
app.setPalette(pal)

view = QQuickView()
view.setSource(QUrl.fromLocalFile('test_palette.qml'))

print("Palette Window:", app.palette().window().color().name())
print("QQuickView clear color:", view.color().name())
