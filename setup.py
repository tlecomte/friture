# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools.extension import Extension
from os.path import join, dirname  # for README content reading
import friture  # for the version number

# see INSTALL file for details
# to create a source package
#       python setup.py sdist --formats=gztar
# to upload a new release to the test instance of PyPI
#       twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# to upload the new release to PyPI
# Warning: the 'dist' folder should be clean !
#       twine upload dist/*

# to test for pep8 issues:
# pycodestyle --show-source --show-pep8 --max-line-length=170 friture

# to fix pep8 issues automatically (replace -d by -i if the changes are fine):
# autopep8 --max-line-length=170 -d -r friture

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
    "sounddevice==0.4.2",
    "rtmixer==0.1.3",
    "PyOpenGL==3.1.5",
    "PyOpenGL-accelerate==3.1.5",
    "docutils==0.17.1",
    "numpy==1.21.1",
    "PyQt5==5.15.4",
    "appdirs==1.4.4",
    "pyrr==0.10.3",
]

# Cython and numpy are needed when running setup.py, to build extensions
setup_requires=["numpy==1.21.1", "Cython==0.29.24"]

with open(join(dirname(__file__), 'README.rst')) as f:
    long_description = f.read()

setup(name="friture",
      version=friture.__version__,
      description='Real-time visualization of live audio data',
      long_description=long_description,
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
      data_files = [('share/applications', ['appimage/friture.desktop'])],
)
