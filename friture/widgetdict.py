#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

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

from friture.levels import Levels_Widget
from friture.spectrum import Spectrum_Widget
from friture.spectrogram import Spectrogram_Widget
from friture.octavespectrum import OctaveSpectrum_Widget
from friture.scope import Scope_Widget
from friture.generator import Generator_Widget
from friture.delay_estimator import Delay_Estimator_Widget
from friture.longlevels import LongLevelWidget

widgetDictionary = {
    0: Levels_Widget,
    1: Scope_Widget,
    2: Spectrum_Widget,
    3: Spectrogram_Widget,
    4: OctaveSpectrum_Widget,
    5: Generator_Widget,
    6: Delay_Estimator_Widget,
    7: LongLevelWidget
    }
