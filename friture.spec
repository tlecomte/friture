# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

sounddevice_data = collect_data_files("sounddevice", subdir="_sounddevice_data")
libportaudio = [(file[0], "_sounddevice_data") for file in sounddevice_data if "libportaudio" in file[0]]

a = Analysis(['main.py'],
             pathex=[],
             binaries=None,
             datas=libportaudio,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=["matplotlib", "PIL", "IPython", "tornado", "zmq", "numpy.core._dotblas"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='friture',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon="resources/images/friture.ico")
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='friture')
