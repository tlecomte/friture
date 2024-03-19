#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

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
import os.path
import numpy as np
import unittest

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    np.set_printoptions(threshold=1024)
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__), '*.py')
    unittest.TextTestRunner(verbosity=2).run(suite)
