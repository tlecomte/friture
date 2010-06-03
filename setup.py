# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe
from glob import glob

# to build an executable for Windows, run 'python setup.py py2exe'

data_files = [("imageformats", glob(r'C:\Python*\Lib\site-packages\PyQt4\plugins\imageformats\qsvg4.dll'))]

setup(windows=[{"script":'friture.py', "icon_resources":[(1, "window-icon.ico")]}],
	  options={"py2exe":{"includes":["sip", "PyQt4.QtSvg"],
						 "excludes":["matplotlib","_ssl","Tkconstants","Tkinter","tcl"],
						 "dll_excludes":["powrprof.dll"]}},
	  data_files=data_files)
