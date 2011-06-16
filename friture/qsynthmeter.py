#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2004-2007, rncbc aka Rui Nuno Capela.
# Copyright (C) 2009 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http:#www.gnu.org/licenses/>.

from PyQt4 import QtCore, QtGui
from numpy import log10

# Meter level limits (in dB).
QSYNTH_METER_MAXDB = +3.
QSYNTH_METER_MINDB = -70.

# The decay rates (magic goes here :).
# - value decay rate (faster)
#QSYNTH_METER_DECAY_RATE1 = 1.0 - 3E-2
# - peak decay rate (slower)
QSYNTH_METER_DECAY_RATE2 = 1.0 - 3E-6

# Number of cycles the peak stays on hold before fall-off.
QSYNTH_METER_PEAK_FALLOFF = 32 # default : 16


#----------------------------------------------------------------------------
# qsynthMeterScale -- Meter bridge scale widget.

class qsynthMeterScale(QtGui.QWidget):
	# Constructor.
	def __init__(self, pMeter):
		QtGui.QWidget.__init__(self, pMeter)
		self.m_pMeter = pMeter
		self.m_iLastY = 0

		self.setMinimumWidth(16)
		#self.setBackgroundRole(QPalette.Mid)

		self.setFont(QtGui.QFont(self.font().family(), 5))

	# Draw IEC scale line and label assumes labels drawed from top to bottom.
	def drawLineLabel(self, p, y, sLabel):
		iCurrY = self.height() - y
		iWidth = self.width()  #- 2

		fm = p.fontMetrics()
		iMidHeight = fm.height()/2 # >> 1)

		if iCurrY < iMidHeight or iCurrY > self.m_iLastY + iMidHeight:
			if fm.width(sLabel) < iWidth - 5:
				p.drawLine(0, iCurrY, 2, iCurrY)
				if self.m_pMeter.portCount() > 1:
					p.drawLine(iWidth - 3, iCurrY, iWidth - 1, iCurrY)
			p.drawText(0, iCurrY - iMidHeight, iWidth-1, fm.height(),
				QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, sLabel)
			self.m_iLastY = iCurrY + 1

	# Paint event handler.
	def paintEvent (self, event):
		p = QtGui.QPainter(self)

		self.m_iLastY = 0

		p.setPen(self.palette().mid().color().dark(140))

		for dB in [0, -3, -6, -10, -20, -30, -40, -50, -60]:
			self.drawLineLabel(p, self.m_pMeter.iec_scale(dB), str(abs(dB)))


#----------------------------------------------------------------------------
# qsynthMeterValue -- Meter bridge value widget.
class qsynthMeterValue(QtGui.QFrame):
	# Constructor.
	def __init__(self, pMeter):
		QtGui.QFrame.__init__(self, pMeter)
		
		# Local instance variables.
		self.m_pMeter      = pMeter
		self.m_fValue      = 0.0
		self.m_iValue  = 0
		#self.m_fValueDecay = QSYNTH_METER_DECAY_RATE1
		self.m_iPeak       = 0
		self.m_iPeakHold   = 0
		self.m_fPeakDecay  = QSYNTH_METER_DECAY_RATE2
		self.m_iPeakColor  = self.m_pMeter.Color6dB

		self.paint_time = 0.

		self.setMinimumWidth(12)
		self.setBackgroundRole(QtGui.QPalette.NoRole)

	# Reset peak holder.
	def peakReset(self):
		self.m_iPeak = 0

	# Frame value one-way accessors.
	def setValue(self, fValue):
		self.m_fValue = fValue
		self.refresh()

	# Value refreshment.
	def refresh(self):
		dB = self.m_fValue
		
		if dB < QSYNTH_METER_MINDB:
			dB = QSYNTH_METER_MINDB
		elif dB > QSYNTH_METER_MAXDB:
			dB = QSYNTH_METER_MAXDB

		iValue = self.m_pMeter.iec_scale(dB)
		#if iValue < self.m_iValue:
			#iValue = int(self.m_fValueDecay * float(self.m_iValue))
			#self.m_fValueDecay *= self.m_fValueDecay
		#else:
			#self.m_fValueDecay = QSYNTH_METER_DECAY_RATE1

		iPeak = self.m_iPeak
		if iPeak < iValue:
			iPeak = iValue
			self.m_iPeakHold = 0
			self.m_fPeakDecay = QSYNTH_METER_DECAY_RATE2
			self.m_iPeakColor = self.m_pMeter.Color10dB #iLevel
			while self.m_iPeakColor > self.m_pMeter.ColorOver and iPeak >= self.m_pMeter.iec_level(self.m_iPeakColor):
				self.m_iPeakColor -= 1
		elif self.m_iPeakHold + 1 > self.m_pMeter.peakFalloff():
			iPeak = self.m_fPeakDecay * float(iPeak)
			if self.m_iPeak < iValue:
				iPeak = iValue
			else:
				#if iPeak < self.m_pMeter.iec_level(self.m_pMeter.Color10dB):
					#self.m_iPeakColor = self.m_pMeter.Color6dB
				self.m_fPeakDecay *= self.m_fPeakDecay
		self.m_iPeakHold += 1

		if iValue == self.m_iValue and iPeak == self.m_iPeak:
			return

		self.m_iValue = iValue
		self.m_iPeak  = iPeak

		self.update()

	# Paint event handler.
	def paintEvent(self, event):
		t = QtCore.QTime()
		t.start()
		
		painter = QtGui.QPainter(self)

		w = self.width()
		h = self.height()

		if self.isEnabled():
			painter.fillRect(0, 0, w, h,
				self.m_pMeter.color(self.m_pMeter.ColorBack))
			y = self.m_pMeter.iec_level(self.m_pMeter.Color0dB)
			painter.setPen(self.m_pMeter.color(self.m_pMeter.ColorFore))
			painter.drawLine(0, h - y, w, h - y)
		else:
			painter.fillRect(0, 0, w, h, self.palette().dark().color())

		if 1: #CONFIG_GRADIENT
			painter.drawPixmap(0, h - self.m_iValue,
				self.m_pMeter.pixmap(), 0, h - self.m_iValue, w, self.m_iValue + 1)
	  	else:
			y = self.m_iValue

			y_over = 0
			y_curr = 0

			i = self.m_pMeter.Color10dB
			while i > self.m_pMeter.ColorOver and y >= y_over:
				y_curr = self.m_pMeter.iec_level(i)

				if y < y_curr:
					painter.fillRect(0, h - y, w, y - y_over,
						self.m_pMeter.color(i))
				else:
					painter.fillRect(0, h - y_curr, w, y_curr - y_over,
						self.m_pMeter.color(i))
				y_over = y_curr
				i -= 1

			if y > y_over:
				painter.fillRect(0, h - y, w, y - y_over,
					self.m_pMeter.color(self.m_pMeter.ColorOver))

		painter.setPen(self.m_pMeter.color(self.m_iPeakColor))
		painter.drawLine(0, h - self.m_iPeak, w, h - self.m_iPeak)
		
		self.paint_time = (95.*self.paint_time + 5.*t.elapsed())/100.

	# Resize event handler.
	def resizeEvent(self, pResizeEvent):
		self.m_iPeak = 0

		QtGui.QWidget.resizeEvent(self, pResizeEvent)
		#QtGui.QWidget.repaint(true)


#----------------------------------------------------------------------------
# qsynthMeter -- Meter bridge slot widget.

class qsynthMeter(QtGui.QFrame):
	# Constructor.
	def __init__(self, pParent):
		QtGui.QFrame.__init__(self, pParent)
		
		# Local instance variables.
		self.m_iPortCount   = 2	# FIXME: Default port count.
		self.m_iScaleCount  = self.m_iPortCount

		self.m_fScale = 0.

		if 1: #CONFIG_GRADIENT
			self.m_pPixmap = QtGui.QPixmap()

		# Peak falloff mode setting (0=no peak falloff).
		self.m_iPeakFalloff = QSYNTH_METER_PEAK_FALLOFF
			
		self.ColorOver	= 0
		self.Color0dB	= 1
		self.Color3dB	= 2
		self.Color6dB	= 3
		self.Color10dB	= 4
		self.LevelCount	= 5
		self.ColorBack	= 5
		self.ColorFore	= 6
		self.ColorCount	= 7
		
		self.m_levels = [0]*self.LevelCount

		self.m_colors = [QtGui.QColor(0,  0, 0)]*self.ColorCount
		self.m_colors[self.ColorOver] = QtGui.QColor(240,  0, 20)
		self.m_colors[self.Color0dB]  = QtGui.QColor(240,160, 20)
		self.m_colors[self.Color3dB]  = QtGui.QColor(220,220, 20)
		self.m_colors[self.Color6dB]  = QtGui.QColor(160,220, 20)
		self.m_colors[self.Color10dB] = QtGui.QColor( 40,160, 40)
		self.m_colors[self.ColorBack] = QtGui.QColor( 20, 40, 20)
		self.m_colors[self.ColorFore] = QtGui.QColor( 80, 80, 80)

		self.setBackgroundRole(QtGui.QPalette.NoRole)

		self.m_pHBoxLayout = QtGui.QHBoxLayout()
		self.m_pHBoxLayout.setMargin(0)
		self.m_pHBoxLayout.setSpacing(0)
		self.setLayout(self.m_pHBoxLayout)

		self.build()

		self.setSizePolicy(
			QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

	# build the widget layout depending on the port count.
	def build(self):
		while self.m_pHBoxLayout.count() > 0:
			item = self.m_pHBoxLayout.takeAt(0)
			if not item:
				continue

			w = item.widget()
			if w:
				w.deleteLater()

		if self.m_iPortCount > 0 and self.m_iPortCount < 4:
			self.m_iScaleCount = 1
			self.m_ppValues = []
			self.m_ppScales = []
			for iPort in range(0, self.m_iPortCount):
				self.m_ppValues += [qsynthMeterValue(self)]
				self.m_pHBoxLayout.addWidget(self.m_ppValues[iPort])
				if iPort < self.m_iScaleCount:
					self.m_ppScales += [qsynthMeterScale(self)]
					self.m_pHBoxLayout.addWidget(self.m_ppScales[iPort])
			self.setMinimumSize(16 * self.m_iPortCount + 16 * self.m_iScaleCount, 120)
			self.setMaximumWidth(16 * self.m_iPortCount + 16 * self.m_iScaleCount)
		elif self.m_iPortCount >= 4:
			self.m_iScaleCount = 1
			self.m_ppValues = []
			self.m_ppScales = []
			for iPort in range(0, self.m_iPortCount):
				self.m_ppValues += [qsynthMeterValue(self)]
				self.m_pHBoxLayout.addWidget(self.m_ppValues[iPort])
				if iPort == 1:
					self.m_ppScales += [qsynthMeterScale(self)]
					self.m_pHBoxLayout.addWidget(self.m_ppScales[-1])
				if iPort % 2 == 0:
					self.m_pHBoxLayout.addSpacing(1)
			self.setMinimumSize(16 * self.m_iPortCount + 16 * self.m_iScaleCount, 120)
			self.setMaximumWidth(16 * self.m_iPortCount + 16 * self.m_iScaleCount)
		else:
			self.setMinimumSize(2, 120)
			self.setMaximumWidth(4)

	# Child widget accessors.
	def iec_scale (self, dB ):
		fDef = 1.

		if (dB < -70.0):
			fDef = 0.0
		elif (dB < -60.0):
			fDef = (dB + 70.0) * 0.0025
		elif (dB < -50.0):
			fDef = (dB + 60.0) * 0.005 + 0.025
		elif (dB < -40.0):
			fDef = (dB + 50.0) * 0.0075 + 0.075
		elif (dB < -30.0):
			fDef = (dB + 40.0) * 0.015 + 0.15
		elif (dB < -20.0):
			fDef = (dB + 30.0) * 0.02 + 0.3
		else: # if (dB < 0.0)
			fDef = (dB + 20.0) * 0.025 + 0.5

		return fDef * self.m_fScale


	def iec_level (self, iIndex):
		return self.m_levels[iIndex]


	def portCount (self):
		return self.m_iPortCount

	def setPortCount (self, count):
		self.m_iPortCount = count
    		self.build()

	# Peak falloff mode setting.
	def setPeakFalloff ( self, iPeakFalloff ):
		self.m_iPeakFalloff = iPeakFalloff


	def peakFalloff ( self ):
		return self.m_iPeakFalloff


	# Reset peak holder.
	def peakReset (self):
		for iPort in range (0, self.m_iPortCount):
			self.m_ppValues[iPort].peakReset()

	def pixmap (self):
	  	return self.m_pPixmap

	def updatePixmap (self):
		w = self.width()
		h = self.height()

		grad = QtGui.QLinearGradient(0, 0, 0, h)
		grad.setColorAt(0.2, self.color(self.ColorOver))
		grad.setColorAt(0.3, self.color(self.Color0dB))
		grad.setColorAt(0.4, self.color(self.Color3dB))
		grad.setColorAt(0.6, self.color(self.Color6dB))
		grad.setColorAt(0.8, self.color(self.Color10dB))

		self.m_pPixmap = QtGui.QPixmap(w, h)

		QtGui.QPainter(self.m_pPixmap).fillRect(0, 0, w, h, grad);

	# Slot refreshment.
	def refresh (self):
		for iPort in range (0, self.m_iPortCount):
			self.m_ppValues[iPort].refresh()


	# Resize event handler.
	def resizeEvent ( self, event ):
		self.m_fScale = 0.85 * float(self.height())

		self.m_levels[self.Color0dB]  = self.iec_scale(  0.0)
		self.m_levels[self.Color3dB]  = self.iec_scale( -3.0)
		self.m_levels[self.Color6dB]  = self.iec_scale( -6.0)
		self.m_levels[self.Color10dB] = self.iec_scale(-10.0)

		if 1: #CONFIG_GRADIENT
			self.updatePixmap()

	# Meter value proxy.
	def setValue ( self, iPort, fValue ):
		self.m_ppValues[iPort].setValue(fValue)
		

	# Common resource accessor.
	def color ( self, iIndex ):
		return self.m_colors[iIndex]
