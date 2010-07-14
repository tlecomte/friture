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
from numpy import log10, where, linspace, array
from histplot import HistPlot
import audioproc # audio processing class
import octavespectrum_settings # settings dialog
from filter import load_filters_params, octave_filter_bank_decimation, octave_frequencies
from ringbuffer import RingBuffer

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
SAMPLING_RATE = 44100
NOCTAVE = 8

STYLESHEET = """
QwtPlotCanvas {
	border: 1px solid gray;
	border-radius: 2px;
	background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
	stop: 0 #E0E0E0, stop: 0.5 #FFFFFF);
}
"""

# shared with octavespectrum_settings.py
DEFAULT_SPEC_MIN = -140
DEFAULT_SPEC_MAX = 0
DEFAULT_WEIGHTING = 1 #A
DEFAULT_BANDSPEROCTAVE = 0

class OctaveSpectrum_Widget(QtGui.QWidget):
	def __init__(self, parent, logger = None):
		QtGui.QWidget.__init__(self, parent)

		# store the logger instance
		if logger is None:
		    self.logger = parent.parent.logger
		else:
		    self.logger = logger

		self.audiobuffer = None

		self.setObjectName("Spectrum_Widget")
		self.gridLayout = QtGui.QGridLayout(self)
		self.gridLayout.setObjectName("gridLayout")
		self.PlotZoneSpect = HistPlot(self, self.logger)
		self.PlotZoneSpect.setObjectName("PlotZoneSpect")
		self.gridLayout.addWidget(self.PlotZoneSpect, 0, 0, 1, 1)

		self.setStyleSheet(STYLESHEET)
		
		# initialize the class instance that will do the fft
		self.proc = audioproc.audioproc(self.logger)
		
		self.spec_min = DEFAULT_SPEC_MIN
		self.spec_max = DEFAULT_SPEC_MAX
		self.weighting = DEFAULT_WEIGHTING
		
		bandsperoctave = 3*2**(DEFAULT_BANDSPEROCTAVE-1) if DEFAULT_BANDSPEROCTAVE >= 1 else 1
		self.filters = octave_filters(bandsperoctave)
		self.bankbuffers = [RingBuffer() for band in range(0, bandsperoctave*NOCTAVE)]
		
		# initialize the settings dialog
		self.settings_dialog = octavespectrum_settings.OctaveSpectrum_Settings_Dialog(self, self.logger)

	# method
	def set_buffer(self, buffer):
		self.audiobuffer = buffer

	# method
	def update(self):
		if not self.isVisible():
		    return
		
		#time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000.
		time = 0.135 #FAST setting for a sound level meter
		#time = 1. #SLOW setting for a sound level meter
		
		#get the fresh data
		floatdata = self.audiobuffer.newdata()
		#compute the filters' output
		y, decs = self.filters.filter(floatdata)
		
		#push to the ring buffer
		for bankbuffer, bankdata in zip(self.bankbuffers, y):
			bankbuffer.push(bankdata**2)
		
		#compute the widget data
		#sp = [(dec*bankbuffer.data(time*SAMPLING_RATE/dec)).mean() for bankbuffer, dec in zip(self.bankbuffers, decs)]
		sp = [bankbuffer.data(time*SAMPLING_RATE/dec).mean() for bankbuffer, dec in zip(self.bankbuffers, decs)]
		sp = array(sp)
		
		# Note: the following is largely suboptimal since the filter outputs
		# are computed several times on the same signal...
		#floatdata = self.audiobuffer.data(time*SAMPLING_RATE)
		#y, dec = self.filters.filter(floatdata)
		#sp = [(bank**2).mean() for bank in y]
		#sp = array(sp)[::-1]

		#brute force without decimation
		#y_nodec = octave_filter_bank(self.b, self.a, floatdata)
		#sp_nodec = (y_nodec**2).mean(axis=1)
		
		if self.weighting is 0:
			w = 0.
		elif self.weighting is 1:
			w = self.filters.A
		elif self.weighting is 2:
			w = self.filters.B
		else:
			w = self.filters.C
		
		epsilon = 1e-30
		db_spectrogram = 10*log10(sp + epsilon) + w
		self.PlotZoneSpect.setdata(self.filters.flow, self.filters.fhigh, db_spectrogram)

	def setmin(self, value):
		self.spec_min = value
		self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)
	
	def setmax(self, value):
		self.spec_max = value
		self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)

	def setweighting(self, weighting):
		self.weighting = weighting
		self.PlotZoneSpect.setweighting(weighting)

	def setbandsperoctave(self, bandsperoctave):
		self.filters.setbandsperoctave(bandsperoctave)
		#recreate the ring buffers
		self.bankbuffers = [RingBuffer() for band in range(0, bandsperoctave*NOCTAVE)]

	def settings_called(self, checked):
		self.settings_dialog.show()
	
	def saveState(self, settings):
		self.settings_dialog.saveState(settings)

	def restoreState(self, settings):
		self.settings_dialog.restoreState(settings)

class octave_filters():
	def __init__(self, bandsperoctave):
		self.filters_params = load_filters_params()
		
		[self.bdec, self.adec] = self.filters_params['dec']
				
		self.zfs = None
		
		self.setbandsperoctave(bandsperoctave)

	def filter(self, floatdata):
		y, dec, zfs = octave_filter_bank_decimation(self.bdec, self.adec, self.boct, self.aoct, floatdata)
		#y, dec, zfs = octave_filter_bank_decimation(self.bdec, self.adec, self.boct, self.aoct, floatdata, zis=self.zfs)
		#y, zfs = octave_filter_bank(self.b_nodec, self.a_nodec, floatdata)
		#dec = [1.]*len(y)
		#y, zfs = octave_filter_bank(self.b_nodec, self.a_nodec, floatdata, zis=self.zfs)
		#dec = [1.]*len(y)
		
		self.zfs = zfs
		
		return y, dec
	
	def setbandsperoctave(self, bandsperoctave):
		self.bandsperoctave = bandsperoctave
		self.nbands = NOCTAVE*self.bandsperoctave
		self.fi, self.flow, self.fhigh = octave_frequencies(self.nbands, self.bandsperoctave)
		[self.boct, self.aoct, fi, flow, fhigh] = self.filters_params['%d' %bandsperoctave] 
		
		#z, p, k = tf2zpk(self.bdec, self.adec)
		#print "poles", p, abs(p)**2
		#print "zeros", z, abs(z)**2
		#for b, a in zip(self.boct, self.aoct):
			#z, p, k = tf2zpk(b, a)
			#print "poles", p, abs(p)**2
			#print "zeros", z, abs(z)**2
			
		#[self.b_nodec, self.a_nodec, fi, fl, fh] = octave_filters(self.nbands, self.bandsperoctave)
		
		f = self.fi
		Rc = 12200.**2*f**2 / ((f**2 + 20.6**2)*(f**2 + 12200.**2))
		Rb = 12200.**2*f**3 / ((f**2 + 20.6**2)*(f**2 + 12200.**2)*((f**2 + 158.5**2)**0.5))
		Ra = 12200.**2*f**4 / ((f**2 + 20.6**2)*(f**2 + 12200.**2)*((f**2 + 107.7**2)**0.5) * ((f**2 + 737.9**2)**0.5))         
		self.C = 0.06 + 20.*log10(Rc)
		self.B = 0.17 + 20.*log10(Rb)
		self.A = 2.0  + 20.*log10(Ra)
		self.zfs = None
