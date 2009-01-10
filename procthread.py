#!/usr/bin/env python

############################################################################
# 
#  Copyright (C) 2004-2005 Trolltech AS. All rights reserved.
# 
#  This file is part of the example classes of the Qt Toolkit.
# 
#  This file may be used under the terms of the GNU General Public
#  License version 2.0 as published by the Free Software Foundation
#  and appearing in the file LICENSE.GPL included in the packaging of
#  self file.  Please review the following information to ensure GNU
#  General Public Licensing requirements will be met:
#  http://www.trolltech.com/products/qt/opensource.html
# 
#  If you are unsure which license is appropriate for your use, please
#  review the following information:
#  http://www.trolltech.com/products/qt/licensing.html or contact the
#  sales department at sales@trolltech.com.
# 
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
# 
############################################################################

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
