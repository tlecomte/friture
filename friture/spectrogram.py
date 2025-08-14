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

"""Spectrogram widget, that displays a rolling 2D image of the time-frequency spectrum."""

from PyQt5.QtCore import QObject
from numpy import log10, floor, zeros, float64, tile, array, ndarray
from friture.audiobuffer import AudioBuffer
from friture.imageplot import ImagePlot
from friture.audioproc import audioproc
from friture.signal.color_tranform import Color_Transform
from friture.signal.frequency_resampler import Frequency_Resampler
from friture.signal.online_linear_2D_resampler import Online_Linear_2D_resampler
from friture.signal.transform_pipeline import Transform_Pipeline  # audio processing class
from friture.spectrogram_settings import (Spectrogram_Settings_Dialog,  # settings dialog
                                          DEFAULT_FFT_SIZE,
                                          DEFAULT_FREQ_SCALE,
                                          DEFAULT_MAXFREQ,
                                          DEFAULT_MINFREQ,
                                          DEFAULT_SPEC_MIN,
                                          DEFAULT_SPEC_MAX,
                                          DEFAULT_TIMERANGE,
                                          DEFAULT_WEIGHTING)
import friture.plotting.frequency_scales as fscales

from friture.audiobackend import SAMPLING_RATE, FRAMES_PER_BUFFER, AudioBackend
from fractions import Fraction


class Spectrogram_Widget(QObject):

    def __init__(self, parent):
        super().__init__(parent)

        self.PlotZoneImage = ImagePlot(self)

        self.audiobuffer = None

        # initialize the class instance that will do the fft
        self.proc = audioproc()

        self.frequency_resampler = Frequency_Resampler()
        self.screen_resampler = Online_Linear_2D_resampler()
        self.color_transform = Color_Transform()

        self.audio_pipeline = Transform_Pipeline(
            [
                self.frequency_resampler,
                self.screen_resampler,
                self.color_transform,
            ]
        )

        self.sfft_rate_frac = Fraction(1, 1)

        self.maxfreq = DEFAULT_MAXFREQ
        self.proc.set_maxfreq(self.maxfreq)
        self.minfreq = DEFAULT_MINFREQ
        self.fft_size = 2 ** DEFAULT_FFT_SIZE * 32
        self.proc.set_fftsize(self.fft_size)
        self.spec_min = DEFAULT_SPEC_MIN
        self.spec_max = DEFAULT_SPEC_MAX
        self.weighting = DEFAULT_WEIGHTING

        self.update_weighting()
        self.freq = self.proc.get_freq_scale()
        self.frequency_resampler.setfreq(self.freq)

        self.setfreqscale(fscales.Mel) # matches DEFAULT_FREQ_SCALE = 2 # Mel
        self.frequency_resampler.setfreqrange(self.minfreq, self.maxfreq)

        self.timerange_s = DEFAULT_TIMERANGE

        self.old_index = 0
        self.overlap = 3. / 4.
        self.overlap_frac = Fraction(3, 4)
        self.dT_s = self.fft_size * (1. - self.overlap) / float(SAMPLING_RATE)

        self.PlotZoneImage.setfreqrange(self.minfreq, self.maxfreq)
        self.PlotZoneImage.setspecrange(self.spec_min, self.spec_max)
        self.PlotZoneImage.setweighting(self.weighting)
        self.PlotZoneImage.settimerange(self.timerange_s, self.dT_s)
        self.update_jitter()

        self.sfft_rate_frac = Fraction(SAMPLING_RATE, self.fft_size) / (Fraction(1) - self.overlap_frac) / 1000

        # initialize the settings dialog
        self.settings_dialog = Spectrogram_Settings_Dialog(parent, self)

        self.mustRestart = False

    def qml_file_name(self):
        return self.PlotZoneImage.qml_file_name()

    def view_model(self):
        return self.PlotZoneImage.view_model()

    # method
    def set_buffer(self, buffer: AudioBuffer) -> None:
        self.audiobuffer = buffer
        self.old_index = self.audiobuffer.ringbuffer.offset

    def log_spectrogram(self, sp):
        # Note: implementing the log10 of the array in Cython did not bring
        # any speedup.
        # Idea: Instead of computing the log of the data, I could pre-compute
        # a list of values associated with the colormap, and then do a search...
        epsilon = 1e-30
        return 10. * log10(sp + epsilon)

    # scale the db spectrum from [- spec_range db ... 0 db] to [0..1] (do not clip, will be down after resampling)
    def scale_spectrogram(self, sp):
        return (sp - self.spec_min) / (self.spec_max - self.spec_min)

    def handle_new_data(self, floatdata: ndarray) -> None:
        # we need to maintain an index of where we are in the buffer
        index = self.audiobuffer.ringbuffer.offset

        available = index - self.old_index

        if available < 0:
            # ringbuffer must have grown or something...
            available = 0
            self.old_index = index

        # if we have enough data to add a frequency column in the time-frequency plane, compute it
        needed = self.fft_size * (1. - self.overlap)
        realizable = int(floor(available / needed))

        if realizable > 0:
            spn = zeros((len(self.freq), realizable), dtype=float64)

            for i in range(realizable):
                floatdata = self.audiobuffer.data_indexed(self.old_index, self.fft_size)
                data_time = self.audiobuffer.data_time(self.old_index)

                # for now, take the first channel only
                floatdata = floatdata[0, :]

                # FFT transform
                spn[:, i] = self.proc.analyzelive(floatdata)

                self.old_index += int(needed)

            w = tile(self.w, (1, realizable))
            norm_spectrogram = self.scale_spectrogram(self.log_spectrogram(spn) + w)

            self.screen_resampler.set_height(self.PlotZoneImage.spectrogram_screen_height())
            screen_rate_frac = Fraction(self.PlotZoneImage.spectrogram_screen_width(), int(self.timerange_s * 1000))
            self.screen_resampler.set_ratio(self.sfft_rate_frac, screen_rate_frac)
            self.frequency_resampler.setnsamples(self.PlotZoneImage.spectrogram_screen_height())

            data = self.audio_pipeline.push(norm_spectrogram)

            # ideally we would use the time of the last frame that is really consumed by the FFT processor.
            # it may not be the current time if we don't have enough to compute a FFT window
            self.PlotZoneImage.push(data, data_time)

            if self.mustRestart:
                self.PlotZoneImage.restart()
                self.mustRestart = False

        # thickness of a frequency column depends on FFT size and window overlap
        # hamming window with 75% overlap provides good quality (Perfect reconstruction,
        # aliasing from side lobes only, 42 dB channel isolation)

        # number of frequency columns that we keep depends on the time history that the user has chosen

        # actual displayed spectrogram is a scaled version of the time-frequency plane

    def canvasUpdate(self):
        self.PlotZoneImage.draw()

    def update_jitter(self):
        audio_jitter = 2 * float(FRAMES_PER_BUFFER) / SAMPLING_RATE
        analysis_jitter = self.fft_size * (1. - self.overlap) / SAMPLING_RATE
        total_jitter = audio_jitter + analysis_jitter
        self.PlotZoneImage.set_jitter(total_jitter)

    def pause(self):
        self.PlotZoneImage.pause()

    def restart(self):
        # defer the restart until we get data from the audio source (so that a fresh lastdatatime is passed to the spectrogram image)
        self.mustRestart = True

    def setminfreq(self, freq):
        self.minfreq = freq
        self.PlotZoneImage.setfreqrange(self.minfreq, self.maxfreq)
        self.frequency_resampler.setfreqrange(self.minfreq, self.maxfreq)

    def setmaxfreq(self, freq):
        self.maxfreq = freq
        self.PlotZoneImage.setfreqrange(self.minfreq, self.maxfreq)
        self.frequency_resampler.setfreqrange(self.minfreq, self.maxfreq)
        self.proc.set_maxfreq(freq)
        self.update_weighting()
        self.freq = self.proc.get_freq_scale()
        self.frequency_resampler.setfreq(self.freq)
    
    def setfreqscale(self, freqscale):
        self.PlotZoneImage.setfreqscale(freqscale)
        self.frequency_resampler.setfreqscale(freqscale)

    def setfftsize(self, fft_size):
        self.fft_size = fft_size

        self.proc.set_fftsize(fft_size)
        self.update_weighting()
        self.freq = self.proc.get_freq_scale()
        self.frequency_resampler.setfreq(self.freq)

        self.dT_s = self.fft_size * (1. - self.overlap) / float(SAMPLING_RATE)
        self.PlotZoneImage.settimerange(self.timerange_s, self.dT_s)

        self.sfft_rate_frac = Fraction(SAMPLING_RATE, self.fft_size) / (Fraction(1) - self.overlap_frac) / 1000

        self.update_jitter()

    def setmin(self, value):
        self.spec_min = value
        self.PlotZoneImage.setspecrange(self.spec_min, self.spec_max)

    def setmax(self, value):
        self.spec_max = value
        self.PlotZoneImage.setspecrange(self.spec_min, self.spec_max)

    def setweighting(self, weighting):
        self.weighting = weighting
        self.PlotZoneImage.setweighting(weighting)
        self.update_weighting()

    def update_weighting(self):
        A, B, C = self.proc.get_freq_weighting()
        if self.weighting == 0:
            self.w = array([0.])
        elif self.weighting == 1:
            self.w = A
        elif self.weighting == 2:
            self.w = B
        else:
            self.w = C
        self.w.shape = (len(self.w), 1)

    def settings_called(self, checked):
        self.settings_dialog.show()

    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)

    # slot
    def timerangechanged(self, value):
        self.timerange_s = value
        self.PlotZoneImage.settimerange(self.timerange_s, self.dT_s)
