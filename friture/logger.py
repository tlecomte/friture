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

from PyQt5 import QtCore

__loggerInstance = None

def Logger():
    global __loggerInstance
    if __loggerInstance is None:
        __loggerInstance = __Logger()

    return __loggerInstance

class __Logger(QtCore.QObject):

    logChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.count = 0
        self.log = ""

    # push some text to the log
    def push(self, text):
        if len(self.log) == 0:
            self.log = "[0] %s" % text
        else:
            self.log = "%s\n[%d] %s" % (self.log, self.count, text)
        self.count += 1
        self.logChanged.emit()

        # also print to the console
        print(text, flush=True)

    # return the current log
    def text(self):
        return self.log


# simple logger that prints to the console
class PrintLogger:
    # push some text to the log

    def push(self, text):
        print(text, flush=True)

    # return the current log
    def text(self):
        return ""
