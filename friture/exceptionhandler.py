#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os.path
import time
import io
import traceback
import friture
from PyQt5 import QtCore
from PyQt5 import QtWidgets

def excepthook(exception_type, exception_value, traceback_object):
    # call the standard exception handler to have prints on the console
    sys.__excepthook__(exception_type, exception_value, traceback_object)

    separator = '-' * 80
    log_dir = QtCore.QStandardPaths.standardLocations(QtCore.QStandardPaths.AppDataLocation)[0]
    logFile = os.path.join(log_dir, "friture.log")

    notice = \
        """An unhandled exception occurred. Please report the problem\n"""\
        """on GitHub or via email to <%s>.\n"""\
        """A log has been written to "%s".\n\nError information:\n""" % \
        ("contact@friture.org", logFile)

    versionInfo="Friture " + friture.__versionXXXX__

    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")

    tbinfofile = io.StringIO()
    traceback.print_tb(traceback_object, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = '%s: \n%s' % (str(exception_type), str(exception_value))
    sections = [separator, timeString, separator, errmsg, separator, tbinfo, separator, versionInfo]
    msg = '\n'.join(sections)

    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(logFile, "w") as f:
            f.write(msg)
    except IOError as e:
        print(e)
        pass

    errorbox = QtWidgets.QMessageBox()
    errorbox.setWindowTitle("Friture critical error")
    errorbox.setText(str(notice)+str(msg))
    errorbox.setIcon(QtWidgets.QMessageBox.Critical)
    errorbox.exec_()

sys.excepthook = excepthook
