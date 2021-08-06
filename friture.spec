# -*- mode: python -*-

import os
import platform

import friture  # for the version number
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# pyinstaller is conservative: it includes all Qt5 modules by default
# to reduce our frozen image size, we exclude unused modules
excludes = [
        'PyQt5.QtDeclarative',
        'PyQt5.QtHelp',
        'PyQt5.QtMultimedia',
        'PyQt5.QtNetwork',
        'PyQt5.QtScript',
        'PyQt5.QtScriptTools',
        'PyQt5.QtSql',
        'PyQt5.QtDesigner',
        'PyQt5.QtTest',
        'PyQt5.QtWebKit',
        'PyQt5.QtXMLPatterns',
        'PyQt5.QtCLucene',
        'PyQt5.QtBluetooth',
        'PyQt5.QtConcurrent',
        'PyQt5.QtMultimediaWidgets',
        'PyQt5.QtPositioning',
        'PyQt5.QtQml',
        'PyQt5.QtQuick',
        'PyQt5.QtQuickWidgets',
        'PyQt5.QtSensors',
        'PyQt5.QtSerialPort',
        'PyQt5.QtWebChannel',
        'PyQt5.QtWebEngine',
        'PyQt5.QtWebEngineCore',
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtWebKitWidgets',
        'PyQt5.QtWebSockets']

excluded_binaries = [
        'Qt5DBus.dll',
        'Qt5Location.dll',
        'Qt5Network.dll',
        'Qt5NetworkAuth.dll',
        'Qt5Nfc.dll',
        'Qt5Positioning.dll',
        'Qt5PositioningQuick.dll',
        'Qt5PrintSupport.dll',
        'Qt5Qml.dll',
        'Qt5Quick.dll',
        'Qt5RemoteObjects.dll',
        'Qt5WebSockets.dll',
        'Qt5WinExtras.dll',
        'Qt5Xml.dll',
        'Qt5XmlPatterns.dll',

        # macos
        'QtDeclarative.framework',
        'QtHelp.framework',
        'QtMultimedia.framework',
        'QtNetwork.framework',
        'QtScript.framework',
        'QtScriptTools.framework',
        'QtSql.framework',
        'QtDesigner.framework',
        'QtTest.framework',
        'QtWebKit.framework',
        'QtXMLPatterns.framework',
        'QtCLucene.framework',
        'QtBluetooth.framework',
        'QtConcurrent.framework',
        'QtMultimediaWidgets.framework',
        'QtPositioning.framework',
        'QtQml.framework',
        'QtQuick.framework',
        'QtQuickWidgets.framework',
        'QtSensors.framework',
        'QtSerialPort.framework',
        'QtWebChannel.framework',
        'QtWebEngine.framework',
        'QtWebEngineCore.framework',
        'QtWebEngineWidgets.framework',
        'QtWebKitWidgets.framework',
        'QtWebSockets.framework']

pathex = []
if platform.system() == "Windows":
  # workaround for PyInstaller that does not look where the new PyQt5 official wheels put the Qt dlls
  from PyInstaller.compat import getsitepackages
  pathex += [os.path.join(x, 'PyQt5', 'Qt', 'bin') for x in getsitepackages()]

a = Analysis(['main.py'],
             pathex=pathex,
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=["installer/pyinstaller-hooks"], # our custom hooks for python-sounddevice
             runtime_hooks=[],
             excludes=excludes,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

a.binaries = TOC([x for x in a.binaries if x[0] not in excluded_binaries])

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='friture',
          debug=False,
          strip=False,
          upx=False,
          console=False,
          icon="resources/images/friture.ico")

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='friture')

app = BUNDLE(coll,
         name='friture.app',
         icon='resources/images/friture.icns',
         bundle_identifier="org.silentgain.friture",
         version=friture.__version__,
         info_plist={
            'NSMicrophoneUsageDescription': 'Friture reads from the audio inputs to show visualizations',
            'CFBundleVersion': friture.__version__
         })
