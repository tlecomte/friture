# -*- coding: utf-8 -*-

# A scale engine for logarithmic (base 10) scales
#
# The step size is measured in *decades*
# and the major step size will be adjusted to fit the pattern
# \f$\left\{ 1,2,3,5\right\} \cdot 10^{n}\f$, where n is a natural number
# including zero.
#
# \warning the step size as well as the margins are measured in *decades*.

import numpy as np
from PyQt4.Qwt5 import QwtScaleEngine, QwtScaleTransformation, QwtDoubleInterval, QwtScaleDiv, QwtScaleArithmetic

# Extrema values for logarithmic scales
LOG_MIN = 1.0e-100
LOG_MAX = 1.0e100

class QwtLog10ScaleEngine(QwtScaleEngine):
	def __init__(self, *args):
		QwtScaleEngine.__init__(self, *args)
		self.transf = QwtScaleTransformation(QwtScaleTransformation.Log10)
	
	# Align and divide an interval
	#\param maxNumSteps Max. number of steps
	#\param x1 First limit of the interval (In/Out)
	#\param x2 Second limit of the interval (In/Out)
	#\param stepSize Step size (Out)
	def autoScale(self, maxSteps, x1, x2):#, stepSize):
		print("plouf autoScale")
		if ( x1 > x2 ):
			y = x2.copy()
			x2 = x1
			x1 = y
		
		interval = QwtDoubleInterval(x1 / pow(10.0, lowerMargin()), x2 * pow(10.0, upperMargin()) )
		
		logRef = 1.0
		if reference() > LOG_MIN / 2:
			logRef = min(reference(), LOG_MAX/2)
		
		if testAttribute(QwtScaleEngine.Symmetric):
			delta = max(interval.maxValue() / logRef, logRef / interval.minValue())
			interval.setInterval(logRef / delta, logRef * delta)
		
		if testAttribute(QwtScaleEngine.IncludeReference):
			interval = interval.extend(logRef)
		
		interval = interval.limited(LOG_MIN, LOG_MAX)
		
		if interval.width() == 0.0:
			interval = self.buildInterval(interval.minValue())
		
		stepSize = self.divideInterval(self.log10(interval).width(), max(maxNumSteps, 1))
		stepSize = max(stepSize, 1.0)
		
		if not testAttribute(QwtScaleEngine.Floating):
			interval = self.align(interval, stepSize)
		
		x1 = interval.minValue()
		x2 = interval.maxValue()
		
		if testAttribute(QwtScaleEngine.Inverted):
			y = x2.copy()
			x2 = x1
			x1 = y
			stepSize = -stepSize
		
		return (x1, x2, stepSize)
	
	#Calculate a scale division
	#\param x1 First interval limit 
	#\param x2 Second interval limit 
	#\param maxMajSteps Maximum for the number of major steps
	#\param maxMinSteps Maximum number of minor steps
	#\param stepSize Step size. If stepSize == 0, the scaleEngine calculates one.
	def divideScale(self, x1, x2, maxMajSteps, maxMinSteps, stepSize = 0.0):
		print("plouf divideScale", x1, x2, maxMajSteps, maxMinSteps, stepSize)
		#return QwtScaleDiv(0.,1.,[1,2,3],[],[])
		
		interval = QwtDoubleInterval(x1, x2).normalized().limited(LOG_MIN, LOG_MAX)
		
		if interval.width() <= 0 :
			return QwtScaleDiv()
		
		if interval.maxValue() / interval.minValue() < 10.0:
			# scale width is less than one decade -> build linear scale
			linearScaler = QwtLinearScaleEngine()
			linearScaler.setAttributes(self.attributes())
			linearScaler.setReference(self.reference())
			linearScaler.setMargins(self.lowerMargin(), self.upperMargin())
			return linearScaler.divideScale(x1, x2, maxMajSteps, maxMinSteps, stepSize)
		
		stepSize = abs(stepSize)
		if stepSize == 0.:
			maxMajSteps = max(maxMajSteps, 1)

			stepSize = self.divideInterval(self.log10(interval).width(), maxMajSteps)
			stepSize = max(stepSize, 1.) # major step must be >= 1 decade
		
		scaleDiv = QwtScaleDiv()
		if stepSize != 0.:
			ticks = self.buildTicks(interval, stepSize, maxMinSteps)
			scaleDiv = QwtScaleDiv(interval, ticks[QwtScaleDiv.MajorTick], ticks[QwtScaleDiv.MediumTick], ticks[QwtScaleDiv.MinorTick])
		
		if x1 > x2:
			scaleDiv.invert()
		
		print(scaleDiv.ticks(QwtScaleDiv.MajorTick))
		print(scaleDiv.ticks(QwtScaleDiv.MediumTick))
		print(scaleDiv.ticks(QwtScaleDiv.MinorTick))
		print("plouf finished divideScale")
		
		return scaleDiv
	
	# Return a transformation, for logarithmic (base 10) scales
	def transformation(self):
		import sip
		sip.dump(self.transf)
		print("plouf transformation")
		return self.transf
	
	# Return the interval [log10(interval.minValue(), log10(interval.maxValue]
	def log10(self, interval):
		return QwtDoubleInterval(np.log10(interval.minValue()), np.log10(interval.maxValue()))
	
	# Return the interval [pow10(interval.minValue(), pow10(interval.maxValue]
	def pow10(self, interval):
		return QwtDoubleInterval(pow(10.0, interval.minValue()), pow(10.0, interval.maxValue()))
	
	#Align an interval to a step size
	#The limits of an interval are aligned that both are integer
	#multiples of the step size.
	def align(self, interval, stepSize):
		print("plouf align")
		intv = self.log10(interval)

		x1 = QwtScaleArithmetic.floorEps(intv.minValue(), stepSize)
		x2 = QwtScaleArithmetic.ceilEps(intv.maxValue(), stepSize)

		return self.pow10(QwtDoubleInterval(x1, x2))
	
	def buildTicks(self, interval, stepSize, maxMinSteps):
		boundingInterval = self.align(interval, stepSize)

		ticks = [[]]*QwtScaleDiv.NTickTypes

		ticks[QwtScaleDiv.MajorTick] = self.buildMajorTicks(boundingInterval, stepSize)

		if maxMinSteps > 0:
			ticks[QwtScaleDiv.MinorTick] = self.buildMinorTicks(ticks[QwtScaleDiv.MajorTick], maxMinSteps, stepSize)

		for  i in range(0, QwtScaleDiv.NTickTypes):
			ticks[i] = self.strip(ticks[i], interval)

		print("buildTicks")

		return ticks

	# Remove ticks from a list, that are not inside an interval
	def strip(self, ticks, interval):
		print("strip")
		if (not interval.isValid()) or (len(ticks) == 0) :
			return []

		if self.contains(interval, ticks[0]) and self.contains(interval, ticks[-1]):
			return ticks

		strippedTicks = []
		for i in range(0, len(ticks)):
			if self.contains(interval, ticks[i]):
				strippedTicks += [ticks[i]]
		
		return strippedTicks

	def buildMinorTicks(self, majorTicks, maxMinSteps, stepSize):
		if stepSize < 1.1: # major step width is one decade
			if maxMinSteps < 1:
				return QwtValueList()

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
				for k in range(k0, kmax, kstep):
					minorTicks += [v * float(k)]

			return minorTicks

		else: # major step > one decade
			minStep = self.divideInterval(stepSize, maxMinSteps)
			if minStep == 0.:
				return QwtValueList()

			minStep = max(minStep, 1.)

			# subticks per interval
			nMin = round(stepSize / minStep) - 1

			# Do the minor steps fit into the interval?
			if QwtScaleArithmetic.compareEps((nMin +  1) * minStep, qwtAbs(stepSize), stepSize) > 0:
				nMin = 0

			if nMin < 1:
				return QwtValueList() # no subticks

			# substep factor = 10^substeps
			minFactor = qwtMax(pow(10.0, minStep), 10.0)

			minorTicks = []
			for i in range(0, majorTicks.count()):
				val = majorTicks[i]
				for k in range(0, nMin):
					val *= minFactor
					minorTicks += [val]

			return minorTicks

	def buildMajorTicks(self, interval, stepSize):
		width = self.log10(interval).width()

		numTicks = int(round(width / stepSize) + 1)
		numTicks = min(10000, numTicks)

		lxmin = np.log(interval.minValue())
		lxmax = np.log(interval.maxValue())
		lstep = (lxmax - lxmin) / float(numTicks - 1.)

		ticks = []

		ticks += [interval.minValue()]

		for i in range(1, numTicks):
			ticks += [np.exp(lxmin + float(i) * lstep)]

		ticks += [interval.maxValue()]

		return ticks
	def copy(self):
		print("plouf copy")
		return self