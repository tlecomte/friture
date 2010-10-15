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

SAMPLING_RATE = 44100

# shared with spectrogram.py
DEFAULT_FFT_SIZE = 7 #4096 points
DEFAULT_FREQ_SCALE = 1 #log10
DEFAULT_MAXFREQ = SAMPLING_RATE/2
DEFAULT_MINFREQ = 20
DEFAULT_SPEC_MIN = -140
DEFAULT_SPEC_MAX = 0
DEFAULT_TIMERANGE = 10.
DEFAULT_WEIGHTING = 1 #A

class Spectrogram_Settings_Dialog(QtGui.QDialog):
	def __init__(self, parent, logger):
		QtGui.QDialog.__init__(self, parent)
		
		self.parent = parent
		self.logger = logger
		
		self.setWindowTitle("Spectrogram settings")
		
		self.formLayout = QtGui.QFormLayout(self)
		
		self.doubleSpinBox_timerange = QtGui.QDoubleSpinBox(self)
		self.doubleSpinBox_timerange.setDecimals(1)
		self.doubleSpinBox_timerange.setMinimum(0.1)
		self.doubleSpinBox_timerange.setMaximum(1000.0)
		self.doubleSpinBox_timerange.setProperty("value", DEFAULT_TIMERANGE)
		self.doubleSpinBox_timerange.setObjectName("doubleSpinBox_timerange")
		self.doubleSpinBox_timerange.setSuffix(" s")
		
		self.comboBox_fftsize = QtGui.QComboBox(self)
		self.comboBox_fftsize.setObjectName("comboBox_fftsize")
		self.comboBox_fftsize.addItem("32 points")
		self.comboBox_fftsize.addItem("64 points")
		self.comboBox_fftsize.addItem("128 points")
		self.comboBox_fftsize.addItem("256 points")
		self.comboBox_fftsize.addItem("512 points")
		self.comboBox_fftsize.addItem("1024 points")
		self.comboBox_fftsize.addItem("2048 points")
		self.comboBox_fftsize.addItem("4096 points")
		self.comboBox_fftsize.addItem("8192 points")
		self.comboBox_fftsize.addItem("16384 points")
		self.comboBox_fftsize.setCurrentIndex(DEFAULT_FFT_SIZE)

		self.comboBox_freqscale = QtGui.QComboBox(self)
		self.comboBox_freqscale.setObjectName("comboBox_freqscale")
		self.comboBox_freqscale.addItem("Linear")
		self.comboBox_freqscale.addItem("Logarithmic")
		self.comboBox_freqscale.setCurrentIndex(DEFAULT_FREQ_SCALE)

		self.spinBox_minfreq = QtGui.QSpinBox(self)
		self.spinBox_minfreq.setMinimum(20)
		self.spinBox_minfreq.setMaximum(SAMPLING_RATE/2)
		self.spinBox_minfreq.setSingleStep(10)
		self.spinBox_minfreq.setValue(DEFAULT_MINFREQ)
		self.spinBox_minfreq.setObjectName("spinBox_minfreq")
		self.spinBox_minfreq.setSuffix(" Hz")
		
		self.spinBox_maxfreq = QtGui.QSpinBox(self)
		self.spinBox_maxfreq.setMinimum(20)
		self.spinBox_maxfreq.setMaximum(SAMPLING_RATE/2)
		self.spinBox_maxfreq.setSingleStep(1000)
		self.spinBox_maxfreq.setProperty("value", DEFAULT_MAXFREQ)
		self.spinBox_maxfreq.setObjectName("spinBox_maxfreq")
		self.spinBox_maxfreq.setSuffix(" Hz")

		self.spinBox_specmin = QtGui.QSpinBox(self)
		self.spinBox_specmin.setKeyboardTracking(False)
		self.spinBox_specmin.setMinimum(-200)
		self.spinBox_specmin.setMaximum(200)
		self.spinBox_specmin.setProperty("value", DEFAULT_SPEC_MIN)
		self.spinBox_specmin.setObjectName("spinBox_specmin")
		self.spinBox_specmin.setSuffix(" dB")

		self.spinBox_specmax = QtGui.QSpinBox(self)
		self.spinBox_specmax.setKeyboardTracking(False)
		self.spinBox_specmax.setMinimum(-200)
		self.spinBox_specmax.setMaximum(200)
		self.spinBox_specmax.setProperty("value", DEFAULT_SPEC_MAX)
		self.spinBox_specmax.setObjectName("spinBox_specmax")
		self.spinBox_specmax.setSuffix(" dB")
		
		self.comboBox_weighting = QtGui.QComboBox(self)
		self.comboBox_weighting.setObjectName("weighting")
		self.comboBox_weighting.addItem("None")
		self.comboBox_weighting.addItem("A")
		self.comboBox_weighting.addItem("B")
		self.comboBox_weighting.addItem("C")
		self.comboBox_weighting.setCurrentIndex(DEFAULT_WEIGHTING)

		self.formLayout.addRow("Time range:", self.doubleSpinBox_timerange)
		self.formLayout.addRow("FFT Size:", self.comboBox_fftsize)
		self.formLayout.addRow("Frequency scale:", self.comboBox_freqscale)
		self.formLayout.addRow("Min frequency:", self.spinBox_minfreq)
		self.formLayout.addRow("Max frequency:", self.spinBox_maxfreq)
		self.formLayout.addRow("Min color:", self.spinBox_specmin)
		self.formLayout.addRow("Max color:", self.spinBox_specmax)
		self.formLayout.addRow("Middle-ear weighting:", self.comboBox_weighting)
		
		self.setLayout(self.formLayout)

		self.connect(self.comboBox_fftsize, QtCore.SIGNAL('currentIndexChanged(int)'), self.fftsizechanged)
		self.connect(self.comboBox_freqscale, QtCore.SIGNAL('currentIndexChanged(int)'), self.freqscalechanged)
		self.connect(self.spinBox_minfreq, QtCore.SIGNAL('valueChanged(int)'), self.parent.setminfreq)
		self.connect(self.spinBox_maxfreq, QtCore.SIGNAL('valueChanged(int)'), self.parent.setmaxfreq)
		self.connect(self.spinBox_specmin, QtCore.SIGNAL('valueChanged(int)'), self.parent.setmin)
		self.connect(self.spinBox_specmax, QtCore.SIGNAL('valueChanged(int)'), self.parent.setmax)
		self.connect(self.doubleSpinBox_timerange, QtCore.SIGNAL('valueChanged(double)'), self.parent.timerangechanged)
		self.connect(self.comboBox_weighting, QtCore.SIGNAL('currentIndexChanged(int)'), self.parent.setweighting)

	# slot
	def fftsizechanged(self, index):
		self.logger.push("fft_size_changed slot %d %d %f" %(index, 2**index*32, 150000/2**index*32))
		fft_size = 2**index*32
		self.parent.setfftsize(fft_size)
	
	# slot
	def freqscalechanged(self, index):
		self.logger.push("freq_scale slot %d" %index)
		if index == 1:
			self.parent.PlotZoneImage.setlog10freqscale()
		else:
			self.parent.PlotZoneImage.setlinfreqscale()

	# method
	def saveState(self, settings):
		settings.setValue("timeRange", self.doubleSpinBox_timerange.value())
		settings.setValue("fftSize", self.comboBox_fftsize.currentIndex())
		settings.setValue("freqScale", self.comboBox_freqscale.currentIndex())
		settings.setValue("freqMin", self.spinBox_minfreq.value())
		settings.setValue("freqMax", self.spinBox_maxfreq.value())
		settings.setValue("colorMin", self.spinBox_specmin.value())
		settings.setValue("colorMax", self.spinBox_specmax.value())
		settings.setValue("weighting", self.comboBox_weighting.currentIndex())

	# method
	def restoreState(self, settings):
		(timeRange, ok) = settings.value("timeRange", DEFAULT_TIMERANGE).toDouble()
		self.doubleSpinBox_timerange.setValue(timeRange)
		(fft_size, ok) = settings.value("fftSize", DEFAULT_FFT_SIZE).toInt() # 7th index is 1024 points
		self.comboBox_fftsize.setCurrentIndex(fft_size)
		(freqscale, ok) = settings.value("freqScale", DEFAULT_FREQ_SCALE).toInt()
		self.comboBox_freqscale.setCurrentIndex(freqscale)
		(freqMin, ok) = settings.value("freqMin", DEFAULT_MINFREQ).toInt()
		self.spinBox_minfreq.setValue(freqMin)
		(freqMax, ok) = settings.value("freqMax", DEFAULT_MAXFREQ).toInt()
		self.spinBox_maxfreq.setValue(freqMax)
		(colorMin, ok) = settings.value("colorMin", DEFAULT_SPEC_MIN).toInt()
		self.spinBox_specmin.setValue(colorMin)
		(colorMax, ok) = settings.value("colorMax", DEFAULT_SPEC_MAX).toInt()
		self.spinBox_specmax.setValue(colorMax)
		(weighting, ok) = settings.value("weighting", DEFAULT_WEIGHTING).toInt()
		self.comboBox_weighting.setCurrentIndex(weighting)
