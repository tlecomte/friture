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

from PyQt4 import QtGui, QtCore
from levels import Levels_Widget

class Dock(QtGui.QDockWidget):
	def __init__(self, parent, logger, name):
		QtGui.QDockWidget.__init__(self, name, parent)
		
		self.setObjectName(name)
		
		widget = QtGui.QWidget(self)
		layout = QtGui.QVBoxLayout(widget)
		
		analysis_widget = Levels_Widget(widget)
		analysis_widget.set_buffer(parent.audiobuffer)
		if analysis_widget.update is not None:
			self.connect(parent.display_timer, QtCore.SIGNAL('timeout()'), analysis_widget.update)
		
		layout.addWidget(analysis_widget)
		widget.setLayout(layout)
		self.setWidget(widget)
