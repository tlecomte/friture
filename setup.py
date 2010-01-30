# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe

# to build an executable for Windows, run 'python setup.py py2exe'

setup(windows=['friture.py'], options={"py2exe":{"includes":["sip", "PyQt4.QtSvg"]}})
