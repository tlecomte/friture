# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe
from glob import glob

# to build an executable for Windows, run 'python setup.py py2exe'

#include the QT svg plugin to render the icons
#include the filter coefficients in the pickle file
data_files = [("imageformats", glob(r'C:\Python*\Lib\site-packages\PyQt4\plugins\imageformats\qsvg4.dll')),\
			  ("", glob("generated_filters.pkl"))]
#exclude some python libraries that py2exe includes by error
excludes = ["matplotlib","_ssl","Tkconstants","Tkinter","tcl","email","pyreadline","nose",\
		    "doctest", "pdb", "difflib", "pydoc", "_hashlib", "bz2","httplib","cookielib","cookielib","urllib"]
'_ssl',  # Exclude _ssl
                                #"_ctypes",
                                #'doctest',"pywin", "pywin.debugger", "pywin.debugger.dbgcon",
                                #"pywin.dialogs", "pywin.dialogs.list",
                                #"Tkconstants","Tkinter","tcl",
                                #"compiler","email","ctypes","logging","unicodedata",
                                #'calendar'],  # Exclude standard library
#Note: unittest, inspect are needed by numpy
#exclude dlls that py2exe includes by error
dll_excludes = ["powrprof.dll"]
#manually exclude python libraries that py2exe fails to detect
includes = ["sip", "PyQt4.QtSvg"]

setup(windows=[{"script":'friture.py', "icon_resources":[(1, "window-icon.ico")]}],
	  options={"py2exe":{"includes":includes, "excludes":excludes, "dll_excludes":dll_excludes}},
	  data_files=data_files)
