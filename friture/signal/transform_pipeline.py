#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2023 Timothée Lecomte

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

class Transform_Pipeline:

    def __init__(self, blocks) -> None:
        self.logger = logging.getLogger(__name__)
        self.blocks = blocks

    def push(self, data):

        for block in self.blocks:
            data = block.push(data)

        return data
