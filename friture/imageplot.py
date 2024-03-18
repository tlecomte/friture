#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

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

from PyQt5 import QtCore, QtGui, QtWidgets
from fractions import Fraction
import numpy as np
from friture.audiobackend import AudioBackend
from friture.spectrogram_image import CanvasScaledSpectrogram
from friture.signal.online_linear_2D_resampler import Online_Linear_2D_resampler
from friture.signal.frequency_resampler import Frequency_Resampler
from friture.plotting.scaleWidget import VerticalScaleWidget, HorizontalScaleWidget, ColorScaleWidget
from friture.plotting.scaleDivision import ScaleDivision
from friture.plotting.coordinateTransform import CoordinateTransform
from friture.plotting.canvasWidget import CanvasWidget
import friture.plotting.frequency_scales as fscales


def tickFormatter(value, digits):
    if value >= 1e3:
        label = "%gk" % (value / 1e3)
    else:
        label = "%d" % (value)
    return label


class PlotImage:

    def __init__(self):
        self.canvasscaledspectrogram = CanvasScaledSpectrogram()
        self.T = 0.
        self.dT = 1.

        self.jitter_s = 0.

        self.last_data_time = 0.

        self.isPlaying = True

        self.sfft_rate_frac = Fraction(1, 1)
        self.frequency_resampler = Frequency_Resampler()
        self.resampler = Online_Linear_2D_resampler()

        self.timer = QtCore.QElapsedTimer()
        self.timer.start()

        self.last_time = 0.

    def addData(self, freq, xyzs, freqscale, last_data_time):
        self.frequency_resampler.setfreqscale(freqscale)

        # Note: both the frequency and the time resampler work
        # only on 1D arrays, so we loop on the columns of data.
        # However, we reassemble the 2D output before drawing
        # on the widget's pixmap, because the drawing operation
        # seems to have a costly warmup phase, so it is better
        # to invoke it the fewer number of times possible.

        n = self.resampler.processable(xyzs.shape[1])
        resampled_data = np.zeros((self.frequency_resampler.nsamples, n))

        i = 0
        for j in range(xyzs.shape[1]):
            freq_resampled_data = self.frequency_resampler.process(freq, xyzs[:, j])
            data = self.resampler.process(freq_resampled_data)
            resampled_data[:, i:i + data.shape[1]] = data
            i += data.shape[1]

        self.canvasscaledspectrogram.addData(resampled_data)

        if i > 0:
            self.last_data_time = last_data_time

    def pause(self):
        self.isPlaying = False

    def restart(self):
        self.isPlaying = True
        self.last_time = AudioBackend().get_stream_time()
        self.timer.restart()

    def draw(self, painter, xMap, yMap, rect):
        # update the spectrogram according to possibly new canvas dimensions
        self.frequency_resampler.setnsamples(rect.height())
        self.resampler.set_height(rect.height())
        self.canvasscaledspectrogram.setcanvas_height(rect.height())
        # print self.jitter_s, self.T, rect.width(), rect.width()*(1 + self.jitter_s/self.T)
        jitter_pix = rect.width() * self.jitter_s / self.T
        self.canvasscaledspectrogram.setcanvas_width(rect.width() + jitter_pix)

        screen_rate_frac = Fraction(rect.width(), int(self.T * 1000))
        self.resampler.set_ratio(self.sfft_rate_frac, screen_rate_frac)

        # time advance
        # This function is meant to be called at paintevent time, for better time sync.

        pixmap = self.canvasscaledspectrogram.getpixmap()
        offset = self.canvasscaledspectrogram.getpixmapoffset(delay=jitter_pix / 2)

        if self.isPlaying:
            delta_t = self.timer.nsecsElapsed() * 1e-9
            self.timer.restart()
            pixel_advance = delta_t / (self.T + self.jitter_s) * rect.width()
            self.canvasscaledspectrogram.addPixelAdvance(pixel_advance)

            time = AudioBackend().get_stream_time()
            time_delay = time - self.last_data_time
            pixel_delay = rect.width() * time_delay / self.T

            self.last_time = time

            offset += pixel_delay

        rolling = True
        if rolling:
            # draw the whole canvas with a selected portion of the pixmap

            hints = painter.renderHints()
            # enable bilinear pixmap transformation
            painter.setRenderHints(hints | QtGui.QPainter.SmoothPixmapTransform)
            # Note: nstead of a generic bilinear transformation, a specialized one could be more efficient,
            # since no transformation is needed in y, and the sampling rate is already known to be ok in x.
            sw = rect.width()
            sh = rect.height()

            source_rect = QtCore.QRectF(offset, 0, sw, sh)
            # QRectF since the offset and width may be non-integer
            painter.drawPixmap(QtCore.QRectF(rect), pixmap, source_rect)
        else:
            sw = rect.width()
            sh = rect.height()
            source_rect = QtCore.QRectF(0, 0, sw, sh)
            painter.drawPixmap(QtCore.QRectF(rect), pixmap, source_rect)

    def settimerange(self, timerange_seconds, dT):
        self.T = timerange_seconds
        self.dT = dT

    def setfreqrange(self, minfreq, maxfreq):
        self.frequency_resampler.setfreqrange(minfreq, maxfreq)

    def set_sfft_rate(self, rate_frac):
        self.sfft_rate_frac = rate_frac

    def setfreqscale(self, scale):
        self.frequency_resampler.setfreqscale(scale)

    def erase(self):
        self.canvasscaledspectrogram.erase()

    def isOpaque(self):
        return True

    def set_jitter(self, jitter_s):
        self.jitter_s = jitter_s
        # print jitter_s


class ImagePlot(QtWidgets.QWidget):

    def __init__(self, parent):
        super(ImagePlot, self).__init__(parent)

        self.verticalScaleDivision = ScaleDivision(20, 20000)
        self.verticalScaleTransform = CoordinateTransform(20, 20000, 100, 0, 0)

        self.verticalScale = VerticalScaleWidget(self, self.verticalScaleDivision, self.verticalScaleTransform)
        self.verticalScale.setTitle("Frequency (Hz)")
        self.verticalScale.scaleBar.setTickFormatter(tickFormatter)

        self.horizontalScaleDivision = ScaleDivision(0, 10)
        self.horizontalScaleTransform = CoordinateTransform(0, 10, 100, 0, 0)

        self.horizontalScale = HorizontalScaleWidget(self, self.horizontalScaleDivision, self.horizontalScaleTransform)
        self.horizontalScale.setTitle("Time (s)")

        self.colorScaleDivision = ScaleDivision(-140, 0)
        self.colorScaleTransform = CoordinateTransform(-140, 0, 100, 0, 0)

        self.colorScale = ColorScaleWidget(self, self.colorScaleDivision, self.colorScaleTransform)
        self.colorScale.setTitle("PSD (dB A)")

        self.canvasWidget = CanvasWidget(self, self.verticalScaleTransform, self.horizontalScaleTransform)
        self.canvasWidget.setTrackerFormatter(self.trackerFormatter)

        plotLayout = QtWidgets.QGridLayout()
        plotLayout.setSpacing(0)
        plotLayout.setContentsMargins(0, 0, 0, 0)
        plotLayout.addWidget(self.verticalScale, 0, 0)
        plotLayout.addWidget(self.canvasWidget, 0, 1)
        plotLayout.addWidget(self.colorScale, 0, 2)
        plotLayout.addWidget(self.horizontalScale, 1, 1)

        self.setLayout(plotLayout)

        self.needfullreplot = False

        # attach a plot image
        self.plotImage = PlotImage()
        self.canvasWidget.attach(self.plotImage)

        self.setfreqscale(fscales.Linear)

        self.setspecrange(-140., 0.)

        # need to replot here for the size Hints to be computed correctly (depending on axis scales...)
        self.update()

    def trackerFormatter(self, x: float, y: float) -> str:
        return f'{x:.2f} s, {y:.0f} Hz ({fscales.freq_to_note(y)})'

    def addData(self, freq, xyzs, last_data_time):
        self.plotImage.addData(freq, xyzs, self.freqscale, last_data_time)

    def draw(self):
        if self.needfullreplot:
            self.needfullreplot = False

            self.verticalScaleTransform.setLength(self.canvasWidget.height())

            self.verticalScale.update()

            self.horizontalScaleTransform.setLength(self.canvasWidget.width())
            startBorder, endBorder = self.horizontalScale.spacingBorders()
            self.horizontalScaleTransform.setBorders(startBorder, endBorder)

            self.horizontalScale.update()

            self.colorScaleTransform.setLength(self.canvasWidget.height())
            startBorder, endBorder = self.colorScale.spacingBorders()
            self.colorScaleTransform.setBorders(startBorder, endBorder)

            self.colorScale.update()

        self.canvasWidget.update()

    # redraw when the widget is resized to update coordinates transformations
    def resizeEvent(self, event):
        self.needfullreplot = True
        self.draw()

    def pause(self):
        self.plotImage.pause()

    def restart(self):
        self.plotImage.restart()

    def setfreqscale(self, scale):
        self.freqscale = scale
        
        self.plotImage.erase()
        self.plotImage.setfreqscale(scale)

        self.verticalScaleTransform.setScale(scale)
        self.verticalScaleDivision.setScale(scale)

        # notify that sizeHint has changed (this should be done with a signal emitted from the scale division to the scale bar)
        self.verticalScale.scaleBar.updateGeometry()

        self.needfullreplot = True
        self.update()

    def settimerange(self, timerange_seconds, dT_seconds):
        self.plotImage.settimerange(timerange_seconds, dT_seconds)

        self.horizontalScaleTransform.setRange(0, timerange_seconds)
        self.horizontalScaleDivision.setRange(0, timerange_seconds)

        # notify that sizeHint has changed (this should be done with a signal emitted from the scale division to the scale bar)
        self.horizontalScale.scaleBar.updateGeometry()

        self.needfullreplot = True
        self.update()

    def set_sfft_rate(self, rate_frac):
        self.plotImage.set_sfft_rate(rate_frac)

    def setfreqrange(self, minfreq, maxfreq):
        self.plotImage.setfreqrange(minfreq, maxfreq)

        self.verticalScaleTransform.setRange(minfreq, maxfreq)
        self.verticalScaleDivision.setRange(minfreq, maxfreq)

        # notify that sizeHint has changed (this should be done with a signal emitted from the scale division to the scale bar)
        self.verticalScale.scaleBar.updateGeometry()

        self.needfullreplot = True
        self.update()

    def setspecrange(self, spec_min, spec_max):
        self.colorScaleTransform.setRange(spec_min, spec_max)
        self.colorScaleDivision.setRange(spec_min, spec_max)

        # notify that sizeHint has changed (this should be done with a signal emitted from the scale division to the scale bar)
        self.colorScale.scaleBar.updateGeometry()

        self.needfullreplot = True
        self.update()

    def setweighting(self, weighting):
        if weighting == 0:
            title = "PSD (dB)"
        elif weighting == 1:
            title = "PSD (dB A)"
        elif weighting == 2:
            title = "PSD (dB B)"
        else:
            title = "PSD (dB C)"

        self.colorScale.setTitle(title)
