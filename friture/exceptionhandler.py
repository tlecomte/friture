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
import logging
import os.path
import time
import io
import traceback
import friture
import appdirs
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QApplication


def fileexcepthook(exception_type, exception_value, traceback_object):
    logger = logging.getLogger(__name__)

    exceptionText = "".join(traceback.format_exception(exception_type, exception_value, traceback_object))
    logger.critical("Unhandled exception: %s", exceptionText)

    versionInfo = "Friture " + friture.__version__
    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")

    # same as in analyzer.py
    logFileName = "friture.log.txt"
    dirs = appdirs.AppDirs("Friture", "")
    logDir = dirs.user_data_dir

    email = "contact@friture.org"

    notice = \
        """<h1>Opps! Something went wrong!</h1>\n\n"""\
        """<p>Sorry, there was an error we could not handle.</p>"""\
        """<p>You can choose to abort, or to ignore the error and try to continue """\
        """(this is not guaranteed to work).</p>"""\
        """<h2>Please help us fix it!</h2>\n\n"""\
        """<p>Please contact us directly via email at <a href="mailto:%s?Subject=Friture%%20acrash report">%s</a> """\
        """and include the log file named <i>%s</i> from the following folder:</p>"""\
        """<p><a href="file:///%s">%s</a></p>"""\
        """<p>Alternatively, if you have a GitHub account, you can create a new issue on <a href="https://github.com/tlecomte/friture/issues">https://github.com/tlecomte/friture/issues</a></p>"""\
        """<h3>Error details</h3>""" % \
        (email, email, logFileName, logDir, logDir)

    msg = notice + timeString + ' (%s)' % versionInfo + '<br>' + exceptionText.replace("\r\n", "\n").replace("\n", "<br>").replace(" ", '&nbsp;')

    return msg


def errorBox(message):
    logger = logging.getLogger(__name__)

    try:
        if QApplication.instance() is None:
            app = QApplication(sys.argv)  # assignment is needed to keep the application alive

        errorbox = QMessageBox()
        errorbox.setWindowTitle("Friture error occured")
        errorbox.setText(message)
        errorbox.setTextFormat(QtCore.Qt.RichText)
        errorbox.setStandardButtons(QMessageBox.Abort)

        continueButton = errorbox.addButton("Ignore and try to continue", QMessageBox.RejectRole)

        ret = errorbox.exec_()

        if ret == QMessageBox.Abort:
            sys.exit(1)
        else:
            logger.info("Try to continue")
    except Exception:
        logger.exception("Failed to display the error box")


def excepthook(exception_type, exception_value, traceback_object):
    gui_message = fileexcepthook(exception_type, exception_value, traceback_object)
    errorBox(gui_message)


sys.excepthook = excepthook
