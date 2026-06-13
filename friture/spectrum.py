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

from PyQt5.QtCore import QObject
from friture.calibrated_display_range import CalibratedDisplayRangeMixin
from friture.spectrum_settings import (Spectrum_Settings_Dialog,  # settings dialog
                                       DEFAULT_FFT_SIZE,
                                       DEFAULT_FREQ_SCALE,
                                       DEFAULT_MAXFREQ,
                                       DEFAULT_MINFREQ,
                                       DEFAULT_SPEC_MIN,
                                       DEFAULT_SPEC_MAX,
                                       DEFAULT_WEIGHTING,
                                       DEFAULT_RESPONSE_TIME,
                                       DEFAULT_SHOW_FREQ_LABELS)
import friture.plotting.frequency_scales as fscales

from friture.ring_buffer_frame_reader import RingBufferFrameReader
from friture.spectrumPlotWidget import SpectrumPlotWidget
from friture.spectrum_frame_analyzer import SpectrumFrameAnalyzer
from friture.global_frequency_calibration import frequency_adjustment_db_for_owner


class Spectrum_Widget(QObject, CalibratedDisplayRangeMixin):

    def __init__(self, parent):
        super().__init__(parent)

        self.audiobuffer = None
        self.PlotZoneSpect = SpectrumPlotWidget(self)

        fft_size = 2 ** DEFAULT_FFT_SIZE * 32
        self.minfreq = DEFAULT_MINFREQ
        self.maxfreq = DEFAULT_MAXFREQ

        self.overlap = 3. / 4.
        self._frame_reader = RingBufferFrameReader(fft_size, self.overlap)
        self._analyzer = SpectrumFrameAnalyzer(
            fft_size=fft_size,
            overlap=self.overlap,
            minfreq=self.minfreq,
            maxfreq=self.maxfreq,
            weighting=DEFAULT_WEIGHTING,
            response_time=DEFAULT_RESPONSE_TIME,
        )

        self.PlotZoneSpect.setfreqscale(fscales.Mel) # matches DEFAULT_FREQ_SCALE = 2 #Mel
        self.PlotZoneSpect.setfreqrange(self.minfreq, self.maxfreq)
        self.init_calibrated_display_range(parent, DEFAULT_SPEC_MIN, DEFAULT_SPEC_MAX)
        self.PlotZoneSpect.setweighting(DEFAULT_WEIGHTING)
        self.PlotZoneSpect.set_peaks_enabled(True)
        self.PlotZoneSpect.set_baseline_displayUnits(0.)
        self.PlotZoneSpect.setShowFreqLabel(DEFAULT_SHOW_FREQ_LABELS)

        # initialize the settings dialog
        self.settings_dialog = Spectrum_Settings_Dialog(parent, self)

    @property
    def proc(self):
        return self._analyzer.proc

    @property
    def fft_size(self):
        return self._analyzer.fft_size

    @property
    def freq(self):
        return self._analyzer.freq

    @property
    def dual_channels(self):
        return self._analyzer.dual_channels

    @dual_channels.setter
    def dual_channels(self, value):
        self._analyzer.set_dual_channels(value)

    @property
    def weighting(self):
        return self._analyzer.weighting

    @weighting.setter
    def weighting(self, value):
        self._analyzer.set_weighting(value)

    @property
    def response_time(self):
        return self._analyzer.response_time

    @response_time.setter
    def response_time(self, value):
        self._analyzer.set_response_time(value)

    def qml_file_name(self):
        return self.PlotZoneSpect.qml_file_name()
    
    def view_model(self):
        return self.PlotZoneSpect.view_model()

    def set_buffer(self, buffer):
        self.audiobuffer = buffer
        self._frame_reader.set_buffer(buffer)

    def handle_new_data(self, floatdata):
        del floatdata
        result = self._analyzer.process_frames(list(self._frame_reader.iter_frames()))
        if result is not None:
            adjustment = frequency_adjustment_db_for_owner(self, result.freq)
            self.PlotZoneSpect.setdata(
                result.freq,
                result.db_spectrogram + adjustment,
                result.fmax_hz,
                result.fpitch_hz,
            )

    def canvasUpdate(self):
        self.PlotZoneSpect.canvasUpdate()

    def pause(self):
        self.PlotZoneSpect.pause()

    def restart(self):
        self.PlotZoneSpect.restart()

    def setresponsetime(self, response_time):
        self.response_time = response_time

    def setminfreq(self, minfreq):
        self.setMinMaxFreq(minfreq, self.maxfreq)

    def setmaxfreq(self, maxfreq):
        self.setMinMaxFreq(self.minfreq, maxfreq)

    def setMinMaxFreq(self, minfreq, maxfreq):
        self.minfreq = minfreq
        self.maxfreq = maxfreq

        realmin = min(self.minfreq, self.maxfreq)
        realmax = max(self.minfreq, self.maxfreq)

        self._analyzer.set_freq_range(minfreq, maxfreq)
        self.PlotZoneSpect.setfreqrange(realmin, realmax)

    def setfftsize(self, fft_size):
        self._analyzer.set_fft_size(fft_size)
        self._frame_reader.set_frame_size(fft_size)
        if self.audiobuffer is not None:
            self._frame_reader.set_buffer(self.audiobuffer)

    def setmin(self, value):
        self.set_base_spec_min(value)

    def setmax(self, value):
        self.set_base_spec_max(value)

    def _apply_calibrated_spec_range(self, spec_min: float, spec_max: float) -> None:
        self.PlotZoneSpect.setspecrange(spec_min, spec_max)

    def setweighting(self, weighting):
        self.weighting = weighting
        self.PlotZoneSpect.setweighting(weighting)

    def setdualchannels(self, dual_enabled):
        self.dual_channels = dual_enabled
        if dual_enabled:
            self.PlotZoneSpect.set_peaks_enabled(False)
            self.PlotZoneSpect.set_baseline_dataUnits(0.)
        else:
            self.PlotZoneSpect.set_peaks_enabled(True)
            self.PlotZoneSpect.set_baseline_displayUnits(0.)

    def setShowFreqLabel(self, showFreqLabel):
        self.PlotZoneSpect.setShowFreqLabel(showFreqLabel)

    def setShowPitchLabel(self, showPitchLabel):
        self.PlotZoneSpect.setShowPitchLabel(showPitchLabel)

    def settings_called(self, checked):
        self.settings_dialog.show()

    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)
