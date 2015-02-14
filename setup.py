# -*- coding: utf-8 -*-
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from glob import glob
import os
from os.path import join, dirname # for README content reading and py2exe fix
import os.path
import numpy
import friture # for the version number

py2exe_build = True
try:
	import py2exe
except ImportError:
	print("Cannot find py2exe")
	py2exe_build = False

# see INSTALL file for details
# to create a source package
#       python setup.py sdist --formats=gztar,zip
# to register a new release on PyPI
#       python setup.py register
# to upload the source files to PyPI after registering
# Warning: the folder should be clean !
#       python setup.py sdist --formats=gztar,zip upload
# to create a bundled windows executable
#       python setup.py py2exe

#NOTE: by default scipy.interpolate.__init__.py and scipy.signal.__init__.py
#import all of their submodules
#To decrease the py2exe distributions dramatically, these import lines can
#be commented out !

data_files = []
excludes = []
dll_excludes = []
includes = []

if py2exe_build:
	# find path to PyQt5 module dir
	import PyQt5
	pyqt5_path = os.path.abspath(PyQt5.__file__)
	pyqt5_dir = os.path.dirname(pyqt5_path)

	#include the Qt SVG plugin to render the icons, and the Qt Windows platform plugin
	svg_plugin = os.path.join(pyqt5_dir, "plugins", "imageformats", "qsvg.dll")
	windows_plugin = os.path.join(pyqt5_dir, "plugins", "platforms", "qwindows.dll")
	data_files += [("imageformats", [svg_plugin]),
					("platforms", [windows_plugin])]

	#exclude some python libraries that py2exe includes by error
	excludes += ["matplotlib","_ssl","Tkconstants","Tkinter","tcl","email","pyreadline","nose",\
			"doctest", "pdb", "pydoc", "_hashlib", "bz2","httplib","cookielib","cookielib","urllib","urllib2","Image",\
			"pywin","optparse","zipfile","calendar","compiler",\
			"_imaging","_ssl"]
	#Note: unittest, inspect are needed by numpy
	#exclude dlls that py2exe includes by error
	#failure to exclude these dlls will prevent the executable to be run under XP for example
	dll_excludes += ["powrprof.dll",
					 "msvcp90.dll",
					 "winnsi.dll",
					 "nsi.dll",
					 "iphlpapi.dll",
					 "WTSAPI32.dll",
					 "API-MS-Win-Core-ErrorHandling-L1-1-0.dll",
					 "API-MS-Win-Core-Misc-L1-1-0.dll",
					 "API-MS-Win-Core-ProcessThreads-L1-1-0.dll",
					 "API-MS-Win-Core-File-L1-1-0.dll",
					 "API-MS-Win-Core-Handle-L1-1-0.dll",
					 "API-MS-Win-Core-Profile-L1-1-0.dll",
					 "API-MS-Win-Core-IO-L1-1-0.dll",
					 "API-MS-Win-Core-String-L1-1-0.dll",
					 "API-MS-Win-Core-Interlocked-L1-1-0.dll",
					 "API-MS-Win-Core-SysInfo-L1-1-0.dll",
					 "API-MS-Win-Security-Base-L1-1-0.dll",
					 "API-MS-Win-Core-LocalRegistry-L1-1-0.dll",
					 "SETUPAPI.dll",
					 "PSAPI.dll",
					 "libifcoremd.dll",
					 "libiomp5md.dll",
					 "libmmd.dll",
					 "msvcp*.dll",
					 "msvcr*.dll"]
	#manually include python libraries that py2exe fails to detect
	# for pyOpenGL : http://www.jstump.com/blog/archive/2009/06/30/py2exe-and-pyopengl-3x-with-no-manual-tinkering/
	# + OpenGL_accelerate.formathandler that is imported by the Python/C
	# API so that py2exe does not detect it
	includes += ["sip",
              "PyQt4.QtSvg",
              "PyQt4.QtXml",
              "OpenGL.platform.win32",
              "OpenGL.arrays.ctypesarrays",
              "OpenGL.arrays.numpymodule",
              "OpenGL.arrays.lists",
              "OpenGL.arrays.numbers",
              "OpenGL.arrays.strings",
              "OpenGL_accelerate.formathandler"]

	if os.name == 'nt':
		if 'CPATH' in os.environ:
			os.environ['CPATH'] = os.environ['CPATH'] + numpy.get_include()
		else:
			os.environ['CPATH'] = numpy.get_include()

ext_modules = [Extension("friture.exp_smoothing_conv", ["friture/extension/exp_smoothing_conv.pyx"],
                         include_dirs = [numpy.get_include()]),
               Extension("friture.linear_interp", ["friture/extension/linear_interp.pyx"],
                         include_dirs = [numpy.get_include()]),
               Extension("friture.lookup_table", ["friture/extension/lookup_table.pyx"],
                         include_dirs = [numpy.get_include()]),
               Extension("friture.norm_square", ["friture/extension/norm_square.pyx"],
                         include_dirs = [numpy.get_include()])]

setup(name = "friture",
	version = friture.__version__,
	description = 'Real-time visualization of live audio data',
	long_description = open(join(dirname(__file__), 'README.rst')).read(),
	license = "GNU GENERAL PUBLIC LICENSE",
	author = 'Timothée Lecomte',
	author_email = 'contact@friture.org',
	url='http://www.friture.org',
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
	packages = ['friture', 'friture.plotting'],
	scripts = ['scripts/friture'],
	windows = [{"script":'friture.py', "icon_resources":[(1, "resources/images/friture.ico")]}],
	options = {"py2exe":{"includes":includes, "excludes":excludes, "dll_excludes":dll_excludes}},
	data_files = data_files,
	cmdclass = {"build_ext": build_ext},
	ext_modules = ext_modules,
	)

# py2exe (0.9.2.2 at least on Python 3.4) does not seem to respect the dll_excludes option
# so we manually remove them from the dist directory
if py2exe_build:
	for filenamePattern in dll_excludes:
		path = join("dist", filenamePattern)
		for filename in glob(path):
			print("Remove %s that py2exe should have excluded." %(filename))
			os.remove(filename)
