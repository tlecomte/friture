import numpy as np

#CoordinateTransform

#transforms between screen coordinates and plot coordinates

class CoordinateTransform(object):
    def __init__(self, min, max, length, startBorder, endBorder):
        super(CoordinateTransform, self).__init__()

        self.min = min
        self.max = max
        self.length = length
        self.startBorder = startBorder
        self.endBorder = endBorder
        self.log = False

    def setRange(self, min, max):
        self.min = min
        self.max = max

    def setLength(self, length):
        self.length = length

    def setBorders(self, start, end):
        self.startBorder = start
        self.endBorder = end

    def setLinear(self):
        self.log = False

    def setLogarithmic(self):
        self.log = True

    def toScreen(self, x):
        if self.max == self.min:
            return self.startBorder + 0.*x # keep x type (this can produce a RunTimeWarning if x contains inf)

        if self.log:
            logMin = max(1e-20, self.min)
            logMax = max(logMin, self.max)
            x = (x<1e-20)*1e-20 + (x>=1e-20)*x
            return (np.log10(x/logMin))*(self.length - self.startBorder - self.endBorder)/np.log10(logMax/logMin) + self.startBorder
        else:
            return (x - self.min)*(self.length - self.startBorder - self.endBorder)/(self.max - self.min) + self.startBorder

    def toPlot(self, x):
        if self.length == self.startBorder + self.endBorder:
            return self.min + 0.*x # keep x type (this can produce a RunTimeWarning if x contains inf)

        if self.log:
            return 10**((x - self.startBorder)*np.log10(self.max/self.min)/(self.length - self.startBorder - self.endBorder))*self.min
        else:
            return (x - self.startBorder)*(self.max - self.min)/(self.length - self.startBorder - self.endBorder) + self.min
