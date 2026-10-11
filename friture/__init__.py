#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Timoth?Lecomte

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

import os

# The pitch tracker runs ~50 small matrix products per second. With one BLAS
# worker per core, OpenBLAS spin-waits between them and keeps every core busy
# while computing slower than a single thread would. Set here, before numpy is
# first imported, so every entry point (main.py, the `friture` script, frozen
# builds) gets it; an explicit value in the environment still wins.
for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")
del _var

# version and date
__version__ = "0.54"
__releasedate__ = "2025-09-14"

__all__ = ["plotting"]
