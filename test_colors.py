from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette
import sys

app = QApplication(sys.argv)
pal = app.palette()
print(pal.color(QPalette.Window).name())
