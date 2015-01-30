from PyQt4 import QtGui, QtCore
from friture.plotting.scaleDivision import numberPrecision

# A widget canvas with a baseline, ticks and tick labels
# The logic of the placement of scale min/max and ticks belongs to another class.
# The title belongs to another class.
class VerticalScaleBar(QtGui.QWidget):
    def __init__(self, parent, division, transform, logger=None):
        super(VerticalScaleBar, self).__init__()

        self.scaleDivision = division
        self.coordinateTransform = transform

        # should be based on font size
        self.tickLength = 8
        self.labelSpacing = 2
        self.borderOffset = 3

        # for vertical scale bar
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum))

    def sizeHint(self):
        # for vertical scale bar
        majorTicks = self.scaleDivision.majorTicks()
        fm = QtGui.QFontMetrics(self.font())

        # label precision
        if len(majorTicks) < 2:
            maxLabelWidth = 0
        else:
            interval = majorTicks[1] - majorTicks[0]
            prec = numberPrecision(interval)
            digits = max(0, int(-prec))
            maxLabelWidth = max([fm.width('{0:.{1}f}'.format(tick, digits)) for tick in majorTicks])

        return QtCore.QSize(maxLabelWidth + self.tickLength + self.borderOffset + self.labelSpacing, 10)

    def set_scale_properties(self, division, transform):
        self.scaleDivision = division
        self.coordinateTransform = transform

        self.update()
        # notify that sizeHint may have changed
        self.updateGeometry()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        fm = painter.fontMetrics()

        # Note: if anti-aliasing is enabled here, then coordinates need to be aligned to half-pixels
        # to get true pixel-aligned lines. Without anti-aliasing, integer coordinates are enough.
        #painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # base line
        xb = self.width() - self.borderOffset
        y0 = self.coordinateTransform.toScreen(self.coordinateTransform.min)
        y1 = self.coordinateTransform.toScreen(self.coordinateTransform.max)
        painter.drawLine(xb, y0, xb, y1)

        # tick start
        xt = xb - self.tickLength
        xtm = xb - self.tickLength/2

        # label end
        le = xt - self.labelSpacing
        lh = fm.height()

        # label precision
        majorTicks = self.scaleDivision.majorTicks()
        if len(majorTicks) < 2:
            interval = 0
        else:
            interval = majorTicks[1] - majorTicks[0]
        precision = numberPrecision(interval)
        digits = max(0, int(-precision))

        for tick in self.scaleDivision.majorTicks():
            # for vertical scale we invert the coordinates
            y = self.height() - self.coordinateTransform.toScreen(tick)
            painter.drawLine(xt, y, xb, y)
            tick_string = '{0:.{1}f}'.format(tick, digits)
            painter.drawText(le - fm.width(tick_string), y + lh/2 - 2, tick_string)

        for tick in self.scaleDivision.minorTicks():
            # for vertical scale we invert the coordinates
            y = self.height() - self.coordinateTransform.toScreen(tick)
            painter.drawLine(xtm, y, xb, y)

    def spacingBorders(self):
        fm = QtGui.QFontMetrics(self.font())
        # for vertical scale bar
        return fm.height()/2, fm.height()/2



class HorizontalScaleBar(QtGui.QWidget):
    def __init__(self, parent, division, transform, logger=None):
        super(HorizontalScaleBar, self).__init__()

        self.scaleDivision = division
        self.coordinateTransform = transform

        # should be based on font size
        self.tickLength = 8
        self.labelSpacing = 2
        self.borderOffset = 3

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed))

    def sizeHint(self):
        # for vertical scale bar
        majorTicks = self.scaleDivision.majorTicks()
        fm = QtGui.QFontMetrics(self.font())

        # label precision
        if len(majorTicks) < 2:
            maxLabelWidth = 0
        else:
            interval = majorTicks[1] - majorTicks[0]
            prec = numberPrecision(interval)
            digits = max(0, int(-prec))
            maxLabelWidth = max([fm.width('{0:.{1}f}'.format(tick, digits)) for tick in majorTicks])

        return QtCore.QSize(10, fm.height() + self.tickLength + self.borderOffset + self.labelSpacing)
        #return QtCore.QSize(maxLabelWidth + self.tickLength + self.borderOffset + self.labelSpacing, 10)

    def set_scale_properties(self, division, transform):
        self.scaleDivision = division
        self.coordinateTransform = transform

        self.update()
        # notify that sizeHint may have changed
        self.updateGeometry()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        fm = painter.fontMetrics()

        # Note: if anti-aliasing is enabled here, then coordinates need to be aligned to half-pixels
        # to get true pixel-aligned lines. Without anti-aliasing, integer coordinates are enough.
        #painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # base line
        yb = self.borderOffset
        x0 = self.coordinateTransform.toScreen(self.coordinateTransform.min)
        x1 = self.coordinateTransform.toScreen(self.coordinateTransform.max)
        painter.drawLine(x0, yb, x1, yb)

        # tick start
        yt = yb + self.tickLength
        ytm = yb + self.tickLength/2

        # label end
        le = yt + self.labelSpacing
        #lh = fm.height()

        # label precision
        majorTicks = self.scaleDivision.majorTicks()
        if len(majorTicks) < 2:
            interval = 0
        else:
            interval = majorTicks[1] - majorTicks[0]
        precision = numberPrecision(interval)
        digits = max(0, int(-precision))

        for tick in self.scaleDivision.majorTicks():
            # for vertical scale we invert the coordinates
            x = self.coordinateTransform.toScreen(tick)
            painter.drawLine(x, yt, x, yb)
            tick_string = '{0:.{1}f}'.format(tick, digits)
            painter.drawText(x - fm.width(tick_string)/2, le + fm.height(), tick_string)

        for tick in self.scaleDivision.minorTicks():
            # for vertical scale we invert the coordinates
            x = self.coordinateTransform.toScreen(tick)
            painter.drawLine(x, ytm, x, yb)

    def spacingBorders(self):
        fm = QtGui.QFontMetrics(self.font())
        # for vertical scale bar
        return fm.height()/2, fm.height()/2