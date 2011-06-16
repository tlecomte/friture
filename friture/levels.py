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

from PyQt4 import QtCore, QtGui
from numpy import log10, abs, arange
from friture.levels_settings import Levels_Settings_Dialog # settings dialog
from friture.qsynthmeter import qsynthMeter
from friture.audioproc import audioproc

from friture.exp_smoothing_conv import pyx_exp_smoothed_value

STYLESHEET = """
qsynthMeter {
border: 1px solid gray;
border-radius: 2px;
padding: 1px;
}
"""

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
SAMPLING_RATE = 44100

class Levels_Widget(QtGui.QWidget):
	def __init__(self, parent = None, logger = None):
		QtGui.QWidget.__init__(self, parent)
		self.setObjectName("Levels_Widget")
		
		self.gridLayout = QtGui.QGridLayout(self)
		self.gridLayout.setObjectName("gridLayout")
		self.label_rms = QtGui.QLabel(self)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setWeight(75)
		font.setBold(True)
		self.label_rms.setFont(font)
		self.label_rms.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing)
		self.label_rms.setObjectName("label_rms")
		self.gridLayout.addWidget(self.label_rms, 0, 0, 1, 1)
		self.meter = qsynthMeter(self)
		self.meter.setStyleSheet(STYLESHEET)
		self.meter.setObjectName("meter")
		self.gridLayout.addWidget(self.meter, 0, 1, 2, 1)
		self.label_peak = QtGui.QLabel(self)
		self.label_peak.setFont(font)
		self.label_peak.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
		self.label_peak.setObjectName("label_peak")
		self.gridLayout.addWidget(self.label_peak, 0, 2, 1, 1)
		self.label_rms_legend = QtGui.QLabel(self)
		self.label_rms_legend.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
		self.label_rms_legend.setObjectName("label_rms_legend")
		self.gridLayout.addWidget(self.label_rms_legend, 1, 0, 1, 1)
		self.label_peak_legend = QtGui.QLabel(self)
		self.label_peak_legend.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
		self.label_peak_legend.setObjectName("label_peak_legend")
		self.gridLayout.addWidget(self.label_peak_legend, 1, 2, 1, 1)

		self.label_rms.setText("-100.0")
		self.label_peak.setText("-100.0")
		self.label_rms_legend.setText("dBFS\n RMS")
		self.label_peak_legend.setText("dBFS\n peak")
		#self.label_rms.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
		#self.label_rms_legend.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
		#self.label_peak.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
		#self.label_peak_legend.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
		
		# store the logger instance
		if logger is None:
		    self.logger = parent.parent.logger
		else:
		    self.logger = logger

		self.audiobuffer = None
		
		# initialize the settings dialog
		self.settings_dialog = Levels_Settings_Dialog(self, self.logger)
		
		# initialize the class instance that will do the fft
		self.proc = audioproc(self.logger)
		
		#time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000. #DISPLAY
		#time = 0.025 #IMPULSE setting for a sound level meter
		#time = 0.125 #FAST setting for a sound level meter
		#time = 1. #SLOW setting for a sound level meter
		self.response_time = 0.125
		# an exponential smoothing filter is a simple IIR filter
		# s_i = alpha*x_i + (1-alpha)*s_{i-1}
		#we compute alpha so that the n most recent samples represent 100*w percent of the output
		w = 0.65
		n = self.response_time*SAMPLING_RATE
		N = 4096
		self.alpha = 1. - (1.-w)**(1./(n+1))
		self.kernel = (1. - self.alpha)**(arange(0, N)[::-1])
		# first channel
		self.old_rms = 1e-30
		self.old_max = 1e-30
		# second channel
		self.old_rms_2 = 1e-30
		self.old_max_2 = 1e-30
		
		n2 = self.response_time/(SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000.)
		self.alpha2 = 1. - (1.-w)**(1./(n2+1))
  
		self.two_channels = False

	# method
	def set_buffer(self, buffer):
		self.audiobuffer = buffer

	# method
	def update(self):
		if not self.isVisible():
			return
		
		# get the fresh data
		floatdata = self.audiobuffer.newdata()

		if floatdata.shape[0] > 1 and self.two_channels == False:
			self.meter.setPortCount(4)
			self.two_channels = True
		elif floatdata.shape[0] == 1 and self.two_channels == True:
			self.meter.setPortCount(2)
			self.two_channels = False

		# first channel
		y1 = floatdata[0,:]
		
		# exponential smoothing for max
		if len(y1) > 0:
			value_max = abs(y1).max()
			if value_max > self.old_max*(1.-self.alpha2):
				self.old_max = value_max
			else:
				# exponential decrease
				self.old_max *= (1.-self.alpha2)
		
		# exponential smoothing for RMS
		value_rms = pyx_exp_smoothed_value(self.kernel, self.alpha, y1**2, self.old_rms)
		self.old_rms = value_rms
		
		level_rms = 10.*log10(value_rms*2. + 0.*1e-80) #*2. to get 0dB for a sine wave
		level_max = 20.*log10(self.old_max + 0.*1e-80)
		if level_rms > -150.:
			string_rms = "%.01f" % level_rms
		else:
			string_rms = "-Inf"
		if level_max > -150.:
			string_peak = "%.01f" % level_max
		else:
			string_peak = "-Inf"

		if not self.two_channels:
			self.meter.setValue(0, level_rms)
			self.meter.setValue(1, level_max)
			self.label_rms.setText(string_rms)
			self.label_peak.setText(string_peak)

		if self.two_channels:
			# second channel
			y2 = floatdata[1,:]
		
			# exponential smoothing for max
			if len(y2) > 0:
				value_max = abs(y2).max()
				if value_max > self.old_max_2*(1.-self.alpha2):
					self.old_max_2 = value_max
				else:
					# exponential decrease
					self.old_max_2 *= (1.-self.alpha2)
			
			# exponential smoothing for RMS
			value_rms = pyx_exp_smoothed_value(self.kernel, self.alpha, y2**2, self.old_rms_2)
			self.old_rms_2 = value_rms
			
			level_rms_2 = 10.*log10(value_rms*2. + 0.*1e-80) #*2. to get 0dB for a sine wave
			level_max_2 = 20.*log10(self.old_max_2 + 0.*1e-80)
			if level_rms_2 > -150.:
				string_rms_2 = "%.01f" % level_rms_2
			else:
				string_rms_2 = "-Inf"
			if level_max > -150.:
				string_peak_2 = "%.01f" % level_max_2
			else:
				string_peak_2 = "-Inf"

			#self.meter.m_iPortCount = 3
			self.meter.setValue(0, level_rms)
			self.meter.setValue(1, level_rms_2)
			self.meter.setValue(2, level_max)
			self.meter.setValue(3, level_max_2)
			self.label_rms.setText("Ch1:\n%s\n\nCh2:\n%s" %(string_rms, string_rms_2))
			self.label_peak.setText("Ch1:\n%s\n\nCh2:\n%s" %(string_peak, string_peak_2))
		
		if 0:
			fft_size = time*SAMPLING_RATE #1024
			maxfreq = SAMPLING_RATE/2
			sp, freq, A, B, C = self.proc.analyzelive(floatdata, fft_size, maxfreq)
			print level_rms, 10*log10((sp**2).sum()*2.), freq.max()

	# slot
	def settings_called(self, checked):
		self.settings_dialog.show()

	# method
	def saveState(self, settings):
		self.settings_dialog.saveState(settings)
	
	# method
	def restoreState(self, settings):
		self.settings_dialog.restoreState(settings)
