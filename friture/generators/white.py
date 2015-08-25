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

import numpy as np
from numpy.random import standard_normal
from PyQt5 import QtWidgets


class WhiteGenerator:
    name = "White noise"

    def __init__(self, parent, logger):
        self.settings = SettingsWidget(parent, logger)

    def settingsWidget(self):
        return self.settings

    def signal(self, t):
        n = len(t)
        return standard_normal(n)


class SettingsWidget(QtWidgets.QWidget):

    def __init__(self, parent, logger):
        super().__init__(parent)

        self.logger = logger

    def saveState(self, settings):
        return

    def restoreState(self, settings):
        return
