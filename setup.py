# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools.extension import Extension
import numpy

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

ext_modules = [Extension("friture_extensions.exp_smoothing_conv",
                    ["friture_extensions/exp_smoothing_conv.pyx"],
                    include_dirs=[numpy.get_include()]),
               Extension("friture_extensions.linear_interp",
                    ["friture_extensions/linear_interp.pyx"],
                    include_dirs=[numpy.get_include()]),
               Extension("friture_extensions.lookup_table",
                    ["friture_extensions/lookup_table.pyx"],
                    include_dirs=[numpy.get_include()]),
               Extension("friture_extensions.lfilter",
                    ["friture_extensions/lfilter.pyx"],
                    include_dirs=[numpy.get_include()])]

setup(ext_modules=ext_modules)
