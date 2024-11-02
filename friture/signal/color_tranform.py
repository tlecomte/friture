#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2018 Timothée Lecomte

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


import logging

import numpy as np
from friture.plotting import generated_cmrmap
from friture_extensions.lookup_table import pyx_color_from_float_2D
from PyQt5.QtGui import QColor

class Color_Transform:

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        # prepare a custom colormap
        self.prepare_palette()

    def prepare_palette(self):
        self.logger.info("palette preparation")

        cmap = generated_cmrmap.CMAP

        self.colors = np.zeros((cmap.shape[0]), dtype=np.uint32)

        for i in range(cmap.shape[0]):
            self.colors[i] = QColor(int(cmap[i, 0] * 255),
                                    int(cmap[i, 1] * 255),
                                    int(cmap[i, 2] * 255)).rgb()

    def push(self, data):
        # clip in [0..1] before using the fast lookup function
        data = np.clip(data, 0., 1.)
        return pyx_color_from_float_2D(self.colors, data)
