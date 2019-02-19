# -*- coding: utf-8 -*-
import sys
from setuptools import setup
from setuptools.extension import Extension
from glob import glob
import os
from os.path import join, dirname  # for README content reading and py2exe fix
import os.path
from pathlib import Path
import friture  # for the version number

py2exe_build = False
py2app_build = False

if "py2exe" in sys.argv:
    try:
        import py2exe
        py2exe_build = True
    except ImportError:
        print("Cannot find py2exe")
elif "py2app" in sys.argv:
    py2app_build = True

# see INSTALL file for details
# to create a source package
#       python setup.py sdist --formats=gztar
# to upload a new release to the test instance of PyPI
#       twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# to upload the new release to PyPI
# Warning: the 'dist' folder should be clean !
#       twine upload dist/*

# to test for pep8 issues:
# pep8 --show-source --show-pep8 --max-line-length=170 friture

# to fix pep8 issues automatically (replace -d by -i if the changes are fine):
# autopep8 --max-line-length=170 -d -r friture

# NOTE: by default scipy.interpolate.__init__.py and scipy.signal.__init__.py
# import all of their submodules
# To decrease the py2exe distributions dramatically, these import lines can
# be commented out !

# icudt53.dll is also huge but needed for Qt
# A stripped down version is available here:
# https://forum.qt.io/topic/37891/minimal-icudt51-dll-icudt52-dll-and-icudt53-dll
# http://qlcplus.sourceforge.net/icudt53.dll

parent_dir = str(Path(os.getcwd()).parent)
dist_dir = os.path.join(parent_dir, 'friture-dist')

# manually include python libraries that py2exe/py2app fails to detect
# for pyOpenGL : http://www.jstump.com/blog/archive/2009/06/30/py2exe-and-pyopengl-3x-with-no-manual-tinkering/
# + OpenGL_accelerate.formathandler that is imported by the Python/C
# API so that py2exe/py2app does not detect it
includes = ["PyQt5.QtSvg",
            "PyQt5.QtXml",
            "OpenGL.platform.win32",
            "OpenGL.arrays.ctypesarrays",
            "OpenGL.arrays.numpymodule",
            "OpenGL.arrays.lists",
            "OpenGL.arrays.numbers",
            "OpenGL.arrays.strings",
            "OpenGL_accelerate.formathandler",
            "_sounddevice_data",
            "sip"]

if py2exe_build:
    data_files = []
    excludes = []
    dll_excludes = []

    # find path to PyQt5 module dir
    import PyQt5
    pyqt5_path = os.path.abspath(PyQt5.__file__)
    pyqt5_dir = os.path.dirname(pyqt5_path)

    # include the Qt SVG plugin to render the icons, and the Qt Windows platform plugin
    svg_plugin = os.path.join(pyqt5_dir, "plugins", "imageformats", "qsvg.dll")
    windows_plugin = os.path.join(pyqt5_dir, "plugins", "platforms", "qwindows.dll")
    data_files += [("imageformats", [svg_plugin]),
                   ("platforms", [windows_plugin])]

    # exclude some python libraries that py2exe includes by error
    excludes += ["matplotlib", "_ssl", "Tkconstants", "Tkinter", "tcl", "email", "pyreadline", "nose",
                 "doctest", "pdb", "pydoc", "_hashlib", "bz2", "httplib", "cookielib", "cookielib", "urllib", "urllib2", "Image",
                 "pywin", "optparse", "zipfile", "calendar", "compiler",
                 "_imaging", "_ssl", "sqlite3", "PIL", "IPython", "tornado", "zmq", "numpy.core._dotblas"]
    # Note: unittest, inspect are needed by numpy
    # exclude dlls that py2exe includes by error
    # failure to exclude these dlls will prevent the executable to be run under XP for example
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
                     "msvcp*.dll",
                     "msvcr*.dll"]

    if os.name == 'nt':
        import numpy
        if 'CPATH' in os.environ:
            os.environ['CPATH'] = os.environ['CPATH'] + numpy.get_include()
        else:
            os.environ['CPATH'] = numpy.get_include()

    extra_options = dict(
        windows=[{"script": 'main.py',
                  "icon_resources": [(1, "resources/images/friture.ico")],
                  "dest_base": "friture"}],
        options={"py2exe": {"includes": includes, "excludes": excludes, "dll_excludes": dll_excludes}},
        data_files=data_files,
    )

elif py2app_build:
    # by default libportaudio.dylib is copied inside the pythonXXX.zip bundle,
    # but a library cannot be loaded from inside such a bundle
    # so copy it explicitely instead
    import sounddevice
    base = os.path.dirname(sounddevice.__file__)
    libportaudio_path = os.path.join(base, "_sounddevice_data", "portaudio-binaries", "libportaudio.dylib")

    # prevent a py2app self-referencing loop by moving the bdist and dist folders out of the current directory
    # see https://stackoverflow.com/questions/7701255/py2app-ioerror-errno-63-file-name-too-long
    py2app_options = {'includes': includes,
                      'iconfile': 'resources/images/friture.icns',
                      'frameworks': [libportaudio_path],
                      'bdist_base': os.path.join(parent_dir, 'friture-build'),
                      'dist_dir': dist_dir}

    extra_options = dict(
        app=['main.py'],
        options={'py2app': py2app_options},
    )
else:
    extra_options = dict()

# solve chicken-and-egg problem that setup.py needs to import Numpy to build the extensions,
# but Numpy is not available until it is installed as a setup dependency
# see: https://stackoverflow.com/a/54128391
class LateIncludeExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.__include_dirs = []
        super().__init__(*args, **kwargs)

    @property
    def include_dirs(self):
        import numpy
        return self.__include_dirs + [numpy.get_include()]

    @include_dirs.setter
    def include_dirs(self, dirs):
        self.__include_dirs = dirs

# extensions
ext_modules = [LateIncludeExtension("friture_extensions.exp_smoothing_conv",
                                    ["friture_extensions/exp_smoothing_conv.pyx"]),
               LateIncludeExtension("friture_extensions.linear_interp",
                                    ["friture_extensions/linear_interp.pyx"]),
               LateIncludeExtension("friture_extensions.lookup_table",
                                    ["friture_extensions/lookup_table.pyx"]),
               LateIncludeExtension("friture_extensions.lfilter",
                                    ["friture_extensions/lfilter.pyx"])]

# Friture runtime dependencies
# these will be installed when calling 'pip install friture'
# they are also retrieved by 'requirements.txt'
install_requires = [
    "sounddevice==0.3.10",
    "PyOpenGL==3.1.0",
    "PyOpenGL-accelerate==3.1.0",
    "docutils==0.14",
    "numpy==1.13.3",
    "PyQt5==5.10.1",
    "appdirs==1.4.3",
    "pyrr==0.9.2",
]

# Cython and numpy are needed when running setup.py, to build extensions
setup_requires=["numpy==1.13.3", "Cython==0.27.3"]

if py2app_build:
    setup_requires.append("py2app")

setup(name="friture",
      version=friture.__version__,
      description='Real-time visualization of live audio data',
      long_description=open(join(dirname(__file__), 'README.rst')).read(),
      license="GNU GENERAL PUBLIC LICENSE",
      author='Timothée Lecomte',
      author_email='contact@friture.org',
      url='http://www.friture.org',
      keywords=["audio", "spectrum", "spectrogram"],
      classifiers=[
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
      packages=['friture',
                'friture.plotting',
                'friture.generators',
                'friture.signal',
                'friture_extensions'],
      scripts=['scripts/friture'],
      ext_modules=ext_modules,
      install_requires=install_requires,
      setup_requires=setup_requires,
      **extra_options
      )

# py2exe (0.9.2.2 at least on Python 3.4) does not seem to respect the dll_excludes option
# so we manually remove them from the dist directory
if py2exe_build:
    for filenamePattern in dll_excludes:
        path = join("dist", filenamePattern)
        for filename in glob(path):
            print("Remove %s that py2exe should have excluded." % (filename))
            os.remove(filename)

# py2app does not respect the dylib_excludes option
# so we manually remove the unused Qt frameworks
if py2app_build:
    print('*** Removing unused Qt frameworks ***')
    framework_dir = os.path.join(dist_dir, "friture.app/Contents/Resources/lib/python{0}.{1}/PyQt5/Qt/lib".format(sys.version_info.major, sys.version_info.minor))
    frameworks = [
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

    for framework in frameworks:
        for root, dirs, files in os.walk(os.path.join(framework_dir, framework)):
            for file in files:
                os.remove(os.path.join(root, file))
