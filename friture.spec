# -*- mode: python -*-

import os
import platform

import friture  # for the version number
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# pyinstaller is conservative: it includes all Qt6 modules by default
# to reduce our frozen image size, we exclude unused modules
excludes = [
        'PyQt6.QtHelp',
        'PyQt6.QtMultimedia',
        'PyQt6.QtSql',
        'PyQt6.QtDesigner',
        'PyQt6.QtTest',
        'PyQt6.QtPositioning',
        'PyQt6.QtSensors',
        'PyQt6.QtSerialPort',
        'PyQt6.QtWebChannel',
        'PyQt6.QtWebEngine',
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebSockets']

excluded_binaries = [
        'Qt6Bluetooth.dll',
        'Qt6DBus.dll',
        'Qt6Location.dll',
        'Qt6Nfc.dll',
        'Qt6Positioning.dll',
        'Qt6PositioningQuick.dll',
        'Qt6PrintSupport.dll',
        'Qt6RemoteObjects.dll',
        'Qt6WebSockets.dll',
        'Qt6WinExtras.dll',
        'Qt6Xml.dll',

        # # macos
        'QtHelp.framework',
        'QtMultimedia.framework',
        'QtSql.framework',
        'QtDesigner.framework',
        'QtTest.framework',
        'QtXMLPatterns.framework',
        'QtBluetooth.framework',
        'QtConcurrent.framework',
        'QtMultimediaWidgets.framework',
        'QtPositioning.framework',
        'QtSensors.framework',
        'QtSerialPort.framework',
        'QtWebChannel.framework',
        'QtWebEngine.framework',
        'QtWebEngineCore.framework',
        'QtWebEngineWidgets.framework',
        'QtWebSockets.framework'
        ]

pathex = []
if platform.system() == "Windows":
  # workaround for PyInstaller that does not look where the new PyQt6 official wheels put the Qt dlls
  from PyInstaller.compat import getsitepackages
  pathex += [os.path.join(x, 'PyQt6', 'Qt', 'bin') for x in getsitepackages()]

a = Analysis(['main.py'],
             pathex=pathex,
             binaries=[],
             datas= [('friture/*.qml', '.' ), ('friture/playback/*.qml', 'playback' ), ('friture/generators/*.qml', 'generators' ), ('friture/*.js', '.' )],
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
