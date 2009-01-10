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

import sys
import numpy
import pyaudio
import audiodata
from PyQt4 import QtCore, QtGui

class AcqThread(QtCore.QThread):

	def __init__(self, parent=None):
		QtCore.QThread.__init__(self, parent)

		self.mutex = QtCore.QMutex()
		self.condition = QtCore.QWaitCondition()

		self.restart = False
		self.abort = False
		self.stop = False
		self.sigcount = 0

	def __del__(self):
		self.mutex.lock()
		self.abort = True
		self.condition.wakeOne()
		self.mutex.unlock()

		self.wait()

	# called from the main thread, will start or wake up the acquisition thread
	def record(self, format, channels, rate, fft_size):
		locker = QtCore.QMutexLocker(self.mutex)

		self.format = format
		self.channels = channels
		self.rate = rate
		self.fft_size = fft_size

		if not self.isRunning():
			self.start()#QtCore.QThread.LowPriority)
		else:
			self.restart = True
			self.condition.wakeOne()

	# ask the record thread to stop recording
	def recordstop(self):
		self.mutex.lock()
		self.stop = True
		self.mutex.unlock()        

	# thread main function
	def run(self):
		#initialize portaudio
		self.p = pyaudio.PyAudio()
		noverflow = 0
		# size in bytes of the audio data acquired at once
		# needs to be equivalent to 20 ms (roughly) for the graphs to be updated @ 50 Hz
		# if rate = 44100 Hz, chunks are made of 44100*0.02 = 882 samples
		chunk = 1024

		while True:
			# (re)read capture parameters
			self.mutex.lock()
			format = self.format
			channels = self.channels
			rate = self.rate
			fft_size = self.fft_size
			self.mutex.unlock()

			if sys.platform == 'darwin':
				channels = 1

			# open the audio stream object
			stream = self.p.open(format = format,
			    channels = channels,
			    rate = rate,
			    input = True,
			    frames_per_buffer = chunk,
			    input_device_index=1)

			print "stream opened, starting capture loop"

			while True:
				self.mutex.lock()
				stop = self.stop
				restart = self.restart
				abort = self.abort
				self.mutex.unlock()

				if stop or restart:
					stream.stop_stream()
					stream.close()
					break

				if abort:
					stream.stop_stream()
					stream.close()
					self.p.terminate()
					return

				try:
					i = 0
					while i<=fft_size/1024:
						data = stream.read(1024)
						adata = audiodata.AudioData(rawdata = data,
									nchannels = channels,
									format = format,
									samplesize = self.p.get_sample_size(format),
									samplerate = rate)
						self.emit(QtCore.SIGNAL("recorded_time"), adata, self.inc_read_signal_count())
						i += 1
		
				except IOError:
					noverflow += 1
					print "capture overflow", noverflow

			self.mutex.lock()
			stop = self.stop
			self.mutex.unlock()
			if stop:
				self.mutex.lock()
				self.condition.wait(self.mutex)
				self.restart = False
				self.stop = False
				self.mutex.unlock()

	def inc_read_signal_count(self):
		locker = QtCore.QMutexLocker(self.mutex)
		self.sigcount += 1
		return self.sigcount

	def read_signal_count(self):
		locker = QtCore.QMutexLocker(self.mutex)
		return self.sigcount
