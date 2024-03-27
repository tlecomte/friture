import os
import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtQuickWidgets import QQuickWidget

def qml_url(fileName):
    return QUrl.fromLocalFile(qml_path(fileName))

def qml_path(fileName):
    # https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(application_path, fileName)

def raise_if_error(quickWidget):
    if quickWidget.status() == QQuickWidget.Error:
        errors = '\n'.join(map(lambda x: x.toString(), quickWidget.errors()))
        raise Exception("QML error(s): %s" % (errors))