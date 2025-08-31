import os
import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtQml import QQmlComponent
from PyQt5.QtQuick import QQuickView

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

def raise_if_error(quickWidget: QQuickWidget) -> None:
    if quickWidget.status() == QQuickWidget.Error:
        errors = '\n'.join(map(lambda x: x.toString(), quickWidget.errors()))
        raise Exception("QML error(s): %s" % (errors))

def view_raise_if_error(quickView: QQuickView) -> None:
    if quickView.status() == QQuickView.Error:
        errors = '\n'.join(map(lambda x: x.toString(), quickView.errors()))
        raise Exception("QML error(s): %s" % (errors))

def component_raise_if_error(component: QQmlComponent) -> None:
    if component.status() == QQmlComponent.Error:
        errors = '\n'.join(map(lambda x: x.toString(), component.errors()))
        raise Exception("QML error(s): %s" % (errors))