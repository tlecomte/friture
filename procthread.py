#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005-2008 Nokia Corporation and/or its subsidiary(-ies).
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

import numpy
import audiodata
import audioproc
from PyQt4 import QtCore

class ProcThread(QtCore.QThread):

	def __init__(self, parent=None):
		QtCore.QThread.__init__(self, parent)

		self.mutex = QtCore.QMutex()
		self.condition = QtCore.QWaitCondition()

		self.restart = False
		self.abort = False

		self.adatabuffer = None

	def __del__(self):
		self.mutex.lock()
		self.abort = True
		self.condition.wakeOne()
		self.mutex.unlock()

		self.wait()

	def process(self, adata, fft_size):
		locker = QtCore.QMutexLocker(self.mutex)

		if adata.nframes < fft_size:
			self.adatabuffer = audiodata.concatenate(self.adatabuffer,adata)
			if self.adatabuffer.nframes < fft_size:
				return
			else:
				self.adata = self.adatabuffer
			self.adatabuffer = None
		else:
			self.adata = adata

		self.fft_size = fft_size

		if not self.isRunning():
			self.start()#QtCore.QThread.LowPriority)
		else:
			self.restart = True
			self.condition.wakeOne()

	def run(self):

		while True:
			# update (synchronize) parameters
			self.mutex.lock()
			adata = self.adata
			fft_size = self.fft_size
			abort = self.abort
			self.mutex.unlock()
			if abort:
				return
		
			spectrograms = None
			for point in numpy.arange(0, adata.nframes/fft_size)*fft_size:
				spe = audioproc.analyzelive(adata, point, fft_size)
				if spectrograms == None:
					spectrograms = spe
				else:
					spectrograms = numpy.vstack((spectrograms,spe))
			
			self.emit(QtCore.SIGNAL("recorded_freq"), spectrograms)
	
			self.mutex.lock()
			restart = self.restart
			self.mutex.unlock()
			if not restart:
				self.mutex.lock()
				self.condition.wait(self.mutex)
				self.restart = False
				self.mutex.unlock()
