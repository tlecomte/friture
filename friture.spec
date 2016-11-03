# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

sounddevice_data = collect_data_files("sounddevice", subdir="_sounddevice_data")
libportaudio = [(file[0], "_sounddevice_data") for file in sounddevice_data if "libportaudio" in file[0]]

# workaround for PyInstaller that does not look where the new PyQt5 official wheels put the Qt dlls
from PyInstaller.compat import getsitepackages
pathex = [os.path.join(x, 'PyQt5', 'Qt', 'bin') for x in getsitepackages()]

a = Analysis(['main.py'],
             pathex=pathex,
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
