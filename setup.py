# -*- coding: utf-8 -*-
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from glob import glob
import os
import numpy

py2exe_build = True
try:
	import py2exe
except ImportError:
	print "Cannot find py2exe"
	py2exe_build = False

# see INSTALL file for details
# to create a source package
#       python setup.py sdist --formats=gztar,zip
# to register a new release on PyPI
#       python setup.py register
# to upload the source files to PyPI after registering
#       python setup.py sdist --formats=gztar,zip upload
# to create a bundled windows executable
#       python setup.py py2exe

data_files = []
excludes = []
dll_excludes = []
includes = []

if py2exe_build:
	#include the QT svg plugin to render the icons
	#include the filter coefficients in the pickle file
	data_files += [("imageformats", glob(r'C:\Python*\Lib\site-packages\PyQt4\plugins\imageformats\qsvg4.dll'))]
	#exclude some python libraries that py2exe includes by error
	excludes += ["matplotlib","_ssl","Tkconstants","Tkinter","tcl","email","pyreadline","nose",\
			"doctest", "pdb", "pydoc", "_hashlib", "bz2","httplib","cookielib","cookielib","urllib","urllib2","Image",\
			"pywin","optparse","zipfile","calendar","compiler",\
			"_imaging","_ssl"]
	#Note: unittest, inspect are needed by numpy
	#exclude dlls that py2exe includes by error
	dll_excludes += ["powrprof.dll", "msvcp90.dll", "winnsi.dll", "nsi.dll", "iphlpapi.dll",
			"API-MS-Win-Core*.dll"]
	#manually include python libraries that py2exe fails to detect
	# for pyOpenGL : http://www.jstump.com/blog/archive/2009/06/30/py2exe-and-pyopengl-3x-with-no-manual-tinkering/
	# + OpenGL_accelerate.formathandler that is imported by the Python/C
	# API so that py2exe does not detect it
	includes += ["sip", "PyQt4.QtSvg", "PyQt4.QtXml",
              "OpenGL.platform.win32",
              "OpenGL.arrays.ctypesarrays",
              "OpenGL.arrays.numpymodule",
              "OpenGL.arrays.lists",
              "OpenGL.arrays.numbers",
              "OpenGL.arrays.strings",
              "OpenGL_accelerate.formathandler"
              ]

	if os.name == 'nt':
		if os.environ.has_key('CPATH'):
			os.environ['CPATH'] = os.environ['CPATH'] + numpy.get_include()
		else:
			os.environ['CPATH'] = numpy.get_include()

ext_modules = [Extension("friture.exp_smoothing_conv", ["friture/extension/exp_smoothing_conv.pyx"],
                         include_dirs = [numpy.get_include()])]

setup(name = "friture",
	version = '0.3',
	description = 'Real-time visualization of live audio data',
	long_description = """\
Friture
-------

Friture is an application to display real-time analysis and visualization of live audio data.

Friture displays audio data in several widgets, such as a scope, a spectrum analyzer, or a rolling 2D spectrogram.

This program can be useful for educational purposes, or to analyze the audio response of a hall, etc.

The name *friture* is a french word for *frying*, also used for *noise* in a sound.
""",
	license = "GNU GENERAL PUBLIC LICENSE",
	author = 'Timothée Lecomte',
	author_email = 'lecomte.timothee@gmail.com',
	url='http://tlecomte.github.com/friture/',
	keywords = ["audio", "spectrum", "spectrogram"],
	classifiers = [
	"Programming Language :: Python",
	"Programming Language :: Cython",
	"Development Status :: 4 - Beta",
	"Environment :: MacOS X",
	"Environment :: Win32 (MS Windows)",
	"Environment :: X11 Applications :: Qt",
	"Intended Audience :: End Users/Desktop",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Operating System :: OS Independent",
	"Topic :: Multimedia :: Sound/Audio :: Analysis",
	"Topic :: Multimedia :: Sound/Audio :: Speech"
	],
	packages = ['friture'],
	scripts = ['scripts/friture'],
	windows = [{"script":'friture.py', "icon_resources":[(1, "resources/images/friture.ico")]}],
	options = {"py2exe":{"includes":includes, "excludes":excludes, "dll_excludes":dll_excludes}},
	data_files = data_files,
	cmdclass = {"build_ext": build_ext},
	ext_modules = ext_modules,
	)
