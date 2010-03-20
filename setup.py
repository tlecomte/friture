# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe

# to build an executable for Windows, run 'python setup.py py2exe'

setup(windows=[{"script":'friture.py', "icon_resources":[(1, "windows-icon.ico")]
}], options={"py2exe":{"includes":["sip", "PyQt4.QtSvg"],"excludes":["matplotlib","_ssl","Tkconstants","Tkinter","tcl"]}})
