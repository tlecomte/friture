# -*- coding: utf-8 -*-
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from glob import glob

try:
	import py2exe
except ImportError:
	print "Cannot find py2exe"

# to build an executable for Windows, run 'python setup.py py2exe'
# to build the cython extension(s), run 'python setup.py build_ext --inplace'

#include the QT svg plugin to render the icons
#include the filter coefficients in the pickle file
data_files = [("imageformats", glob(r'C:\Python*\Lib\site-packages\PyQt4\plugins\imageformats\qsvg4.dll')),\
			  ("", glob("generated_filters.pkl"))]
#exclude some python libraries that py2exe includes by error
excludes = ["matplotlib","_ssl","Tkconstants","Tkinter","tcl","email","pyreadline","nose",\
		    "doctest", "pdb", "difflib", "pydoc", "_hashlib", "bz2","httplib","cookielib","cookielib","urllib","urllib2","Image",\
		    "pywin","optparse","zipfile","calendar","subprocess","compiler",\
		    "_imaging","_ssl"]
#Note: unittest, inspect are needed by numpy
#exclude dlls that py2exe includes by error
dll_excludes = ["powrprof.dll"]
#manually exclude python libraries that py2exe fails to detect
includes = ["sip", "PyQt4.QtSvg"]

ext_modules = [Extension("exp_smoothing_conv", ["exp_smoothing_conv.pyx"])]

setup(name = "Friture",
	windows = [{"script":'friture.py', "icon_resources":[(1, "window-icon.ico")]}],
	options = {"py2exe":{"includes":includes, "excludes":excludes, "dll_excludes":dll_excludes}},
	data_files=data_files,
	cmdclass = {"build_ext": build_ext},
	ext_modules = ext_modules
	)
