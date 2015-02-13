#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import PyQt4.Qwt5 as Qwt
import math

import sys
import sip

LOG2_MIN = 2.**(-20) # Mininum value for logarithmic scales.
LOG2_MAX = 2.**20 # Maximum value for logarithmic scales. 

class CustomScaleEngine(Qwt.QwtScaleEngine):
	def __init__(self):
		Qwt.QwtScaleEngine.__init__(self)

	def transformation(self):
		return CustomScaleTransformation()
        
	def autoScale(self, maxNumSteps, x1, x2):
		if x1 > x2:
			qswap(x1, x2)
		
		base = 2.
		interval = Qwt.QwtDoubleInterval(x1 / pow(base, self.lowerMargin()), x2 * pow(base, self.upperMargin()) )

		logRef = 1.
		if self.reference() > LOG2_MIN / 2:
			logRef = min(self.reference(), LOG2_MAX / 2)
		
		if self.testAttribute(Qwt.QwtScaleEngine.Symmetric):
			delta = max(interval.maxValue() / logRef, logRef / interval.minValue())
			interval.setInterval(logRef / delta, logRef * delta)
		
		if self.testAttribute(Qwt.QwtScaleEngine.IncludeReference):
			interval = interval.extend(logRef)
		
		interval = interval.limited(LOG2_MIN, LOG2_MAX)
		
		if interval.width() == 0.:
			interval = self.buildInterval(interval.minValue())
		
		stepSize = self.divideInterval(self.log2(interval).width(), max(maxNumSteps, 1))
		if stepSize < 1.:
			stepSize = 1.
		
		if not self.testAttribute(Qwt.QwtScaleEngine.Floating):
			interval = self.align(interval, stepSize)
		
		x1 = interval.minValue()
		x2 = interval.maxValue()
		
		if self.testAttribute(Qwt.QwtScaleEngine.Inverted):
			qSwap(x1, x2)
			stepSize = -stepSize
		
		return (x1, x2, stepSize)

	def divideScale(self, x1, x2, maxMajSteps, maxMinSteps, stepSize):
		interval = Qwt.QwtDoubleInterval(x1, x2).normalized()
		interval = interval.limited(LOG2_MIN, LOG2_MAX)
		
		if interval.width() <= 0:
			return Qwt.QwtScaleDiv()
		
		base = 2.
		if interval.maxValue() / interval.minValue() < base:
			# scale width is less than one octave -> build linear scale
			
			linearScaler = Qwt.QwtLinearScaleEngine()
			linearScaler.setAttributes(self.attributes())
			linearScaler.setReference(self.reference())
			linearScaler.setMargins(self.lowerMargin(), self.upperMargin())

			return linearScaler.divideScale(x1, x2, maxMajSteps, maxMinSteps, stepSize)

		stepSize = abs(stepSize)
		
		if stepSize == 0.:
			if maxMajSteps < 1:
				maxMajSteps = 1
			
			stepSize = self.divideInterval(self.log2(interval).width(), maxMajSteps)
			
			if stepSize < 1.:
				stepSize = 1. # major step must be >= 1 decade
		
		scaleDiv = Qwt.QwtScaleDiv()
		
		if stepSize != 0.:
			ticks = self.buildTicks(interval, stepSize, maxMinSteps)
			scaleDiv = Qwt.QwtScaleDiv(interval, ticks[0], ticks[1], ticks[2])
		
		if x1 > x2:
			 scaleDiv.invert()
		
		return scaleDiv

	def buildTicks(self, interval, stepSize, maxMinSteps):
		boundingInterval = self.align(interval, stepSize)
		
		ticks = [[]]*Qwt.QwtScaleDiv.NTickTypes
		
		ticks[Qwt.QwtScaleDiv.MajorTick] = self.buildMajorTicks(boundingInterval, stepSize)
		
		if maxMinSteps > 0:
			ticks[Qwt.QwtScaleDiv.MinorTick] = self.buildMinorTicks(ticks[Qwt.QwtScaleDiv.MajorTick], maxMinSteps, stepSize)
		
		for i in range(0, Qwt.QwtScaleDiv.NTickTypes):
			ticks[i] = self.strip(ticks[i], interval)

		return ticks

	def buildMajorTicks(self, interval, stepSize):
		width = self.log2(interval).width()
		
		numTicks = int(round(width/stepSize)) + 1
		
		if numTicks > 10000:
			numTicks = 10000
		
		base = 2.
		lxmin = math.log(interval.minValue(), base)
		lxmax = math.log(interval.maxValue(), base)
		lstep = (lxmax - lxmin) / float(numTicks - 1)
		
		ticks = []
		
		ticks += [interval.minValue()]
		
		for i in range(1, numTicks-1):
			ticks += [math.pow(base, lxmin + float(i) * lstep)]
		
		ticks += [interval.maxValue()]
		
		return ticks

	def buildMinorTicks(self, majorTicks, maxMinSteps, stepSize):
		if stepSize < 1.1: # major step < one octave
			if (maxMinSteps < 1):
				return []
			
			if maxMinSteps >= 8:
				k0 = 2
				kmax = 9
				kstep = 1
			elif maxMinSteps >= 4:
				k0 = 2
				kmax = 8
				kstep = 2
			elif maxMinSteps >= 2:
				k0 = 2
				kmax = 5
				kstep = 3
			else:
				k0 = 5
				kmax = 5
				kstep = 1

			minorTicks = []

			for i in range(0, len(majorTicks)):
				v = majorTicks[i]
				
				for k in range (k0, kmax, kstep):
					minorTicks += [v * float(k)]

			return minorTicks
		
		else: # major step > one octave
			minStep = self.divideInterval(stepSize, maxMinSteps)
			
			if minStep == 0.:
				return []
			
			if minStep < 1.:
				minStep = 1.
			
			# number of subticks per interval
			nMin = int(round(stepSize / minStep)) - 1
			
			# Do the minor steps fit into the interval?
			if Qwt.QwtScaleArithmetic.compareEps((nMin +  1) * minStep, abs(stepSize), stepSize) > 0:
				nMin = 0
			
			if nMin < 1:
				return [] # no subticks
			
			# substep factor = 2^substeps
			base = 2.
			minFactor = max(pow(base, minStep), base)
			
			minorTicks = []
			for i in range(0, len(majorTicks)):
				val = majorTicks[i]
				
				for k in range(0, nMin):
					val *= minFactor
					minorTicks += [val]
			
			return minorTicks

	def align(self, interval, stepSize):
		intv = self.log2(interval)
		
		x1 = Qwt.QwtScaleArithmetic.floorEps(intv.minValue(), stepSize)
		x2 = Qwt.QwtScaleArithmetic.ceilEps(intv.maxValue(), stepSize)
		
		return self.pow2(Qwt.QwtDoubleInterval(x1, x2))

	def log2(self, interval):
		base = 2.
		return Qwt.QwtDoubleInterval(math.log(interval.minValue(), base), math.log(interval.maxValue(), base))
	
	def pow2(self, interval):
		base = 2.
		return Qwt.QwtDoubleInterval(math.pow(base, interval.minValue()), pow(base, interval.maxValue()))


class CustomScaleTransformation(Qwt.QwtScaleTransformation):
	def __init__(self):
		Qwt.QwtScaleTransformation.__init__(self, Qwt.QwtScaleTransformation.Other)
		self.base = 2.
	
	def copy(self):
		return CustomScaleTransformation()

	def xForm(self, s, s1, s2, p1, p2):
		s = max(s, LOG2_MIN)
		return p1 + (p2 - p1) / math.log(s2 / s1, self.base) * math.log(s / s1, self.base)

	def invXForm(self, p, p1, p2, s1, s2):
		return math.pow(self.base, (p - p1) / (p2 - p1) * math.log(s2 / s1, self.base)) * s1

#just some code to display window...
class window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        
        self.plot = Qwt.QwtPlot()
        self.layout.addWidget(self.plot)
        
        import numpy
        x = numpy.logspace(math.log(20., 2), math.log(20e3, 2), 100., base = 2.)
        y = numpy.random.rand(len(x)) + 1.
        curve = Qwt.QwtPlotCurve()
        curve.attach(self.plot)
        curve.setData(x,y)
        self.plot.setAxisScaleEngine(Qwt.QwtPlot.xBottom, CustomScaleEngine())
        #self.plot.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLinearScaleEngine())
        self.plot.replot()

if __name__ == '__main__':
    #sip.settracemask(0x0007)
    app = QApplication(sys.argv)
    form = window()
    form.resize(800,600)
    form.show()
    app.exec_()
