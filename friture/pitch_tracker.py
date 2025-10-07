#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

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

# Pitch estimator adapted from libf0 (MIT License):
# https://github.com/groupmm/libf0
# Based on SWIPE algorithm by Arturo Camacho:
# Arturo Camacho, John G. Harris; A sawtooth waveform inspired pitch estimator for speech and music. 
# J. Acoust. Soc. Am. 1 September 2008; 124 (3): 1638–1652. https://doi.org/10.1121/1.2951592
# Released under GPLv3 for inclusion in Friture.

from collections.abc import Generator
import logging
import math as m
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings, QObject
from typing import Any, Optional

from friture.audiobackend import SAMPLING_RATE
from friture.audiobuffer import AudioBuffer
from friture.audioproc import audioproc
from friture.curve import Curve
from friture.pitch_tracker_data import PitchTracker_Data, format_frequency, frequency_to_note
from friture.pitch_tracker_settings import (
    DEFAULT_MIN_FREQ,
    DEFAULT_MAX_FREQ,
    DEFAULT_DURATION,
    DEFAULT_FFT_SIZE,
    DEFAULT_MIN_DB,
    DEFAULT_C_RES,
    DEFAULT_P_CONF,
    DEFAULT_P_DELTA,
    PitchTrackerSettingsDialog,
)
from friture.plotting.coordinateTransform import CoordinateTransform
import friture.plotting.frequency_scales as fscales
from friture.ringbuffer import RingBuffer
from friture.store import GetStore

class PitchTrackerWidget(QObject):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)

        self._pitch_tracker_data = PitchTracker_Data(GetStore())

        self._curve = Curve()
        self._curve.name = "Ch1" # type: ignore [assignment]
        self._pitch_tracker_data.add_plot_item(self._curve)

        # cast for qt properties which aren't properly typed
        tracker_data: Any = self._pitch_tracker_data
        tracker_data.vertical_axis.name = "Frequency (Hz)"
        tracker_data.vertical_axis.setTrackerFormatter(
            format_frequency)
        tracker_data.vertical_axis.show_minor_grid_lines = True
        tracker_data.horizontal_axis.name = "Time (sec)"
        tracker_data.horizontal_axis.setTrackerFormatter(
            lambda x: "%#.3g sec" % (x))

        self.min_freq = DEFAULT_MIN_FREQ
        self.max_freq = DEFAULT_MAX_FREQ
        self._pitch_tracker_data.vertical_axis.setRange( # type: ignore
            self.min_freq, self.max_freq)
        self._pitch_tracker_data.vertical_axis.setScale( # type: ignore
            fscales.OctaveC)
        self.vertical_transform = CoordinateTransform(
            self.min_freq, self.max_freq, 1, 0, 0)
        self.vertical_transform.setScale(fscales.OctaveC)

        self.duration = DEFAULT_DURATION
        self._pitch_tracker_data.horizontal_axis.setRange( # type: ignore
            -self.duration, 0.)

        self.settings_dialog = PitchTrackerSettingsDialog(parent, self)

        self.audiobuffer: Optional[AudioBuffer] = None
        self.tracker = PitchTracker(RingBuffer())
        self.update_curve()
    
    def qml_file_name(self) -> str:
        return "PitchView.qml"

    def view_model(self) -> PitchTracker_Data:
        return self._pitch_tracker_data

    # method
    def set_buffer(self, buffer: AudioBuffer) -> None:
        self.audiobuffer = buffer
        self.tracker.set_input_buffer(buffer.ringbuffer)

    def handle_new_data(self, floatdata: np.ndarray) -> None:
        if self.tracker.update():
            self.update_curve()
            self._pitch_tracker_data.pitch = self.tracker.get_latest_estimate() # type: ignore

    def update_curve(self) -> None:
        pitches = self.tracker.get_estimates(self.duration)
        pitches = 1.0 - self.vertical_transform.toScreen(pitches) # type: ignore
        pitches = np.clip(pitches, 0, 1)
        times = np.linspace(0, 1.0, pitches.shape[0])
        self._curve.setData(times, pitches)

    # method
    def canvasUpdate(self) -> None:
        # nothing to do here
        return

    def set_min_freq(self, value: int) -> None:
        self.min_freq = value
        self._pitch_tracker_data.vertical_axis.setRange(self.min_freq, self.max_freq) # type: ignore
        self.vertical_transform.setRange(self.min_freq, self.max_freq)
        self.tracker._init_swipe()  # Reinitialize kernels with new min_freq

    def set_max_freq(self, value: int) -> None:
        self.max_freq = value
        self._pitch_tracker_data.vertical_axis.setRange(self.min_freq, self.max_freq) # type: ignore
        self.vertical_transform.setRange(self.min_freq, self.max_freq)
        self.tracker._init_swipe()  # Reinitialize kernels with new max_freq

    def set_duration(self, value: int) -> None:
        self.duration = value
        self._pitch_tracker_data.horizontal_axis.setRange(-self.duration, 0.) # type: ignore

    def set_min_db(self, value: float) -> None:
        self.tracker.min_db = value

    def set_conf(self, value: float) -> None:
        self.tracker.conf = value

    # slot
    def settings_called(self, checked: bool) -> None:
        self.settings_dialog.show()

    # method
    def saveState(self, settings: QSettings) -> None:
        self.settings_dialog.save_state(settings)

    # method
    def restoreState(self, settings: QSettings) -> None:
        self.settings_dialog.restore_state(settings)

def fastParabolicInterp(y1, y2, y3):
    """Estimate sub-bin pitch offset using parabolic interpolation.

    To increase the precision of the pitch estimate beyond the kernel
    resolution (10 cents), the strongest pitch correlation (y2) and its two
    adjacent values (y1 and y3) are fitted to a parabola. The x-value of
    the vertex represents the positional offset of the "true" pitch
    relative to the center bin, enabling sub-bin pitch accuracy with fewer
    kernels.

    SWIPE's discretized pitch strength values are calculated from an inner
    product of the audio signal with kernels made of cosine lobes. This
    allows the underlying, smooth function to be modeled using a Taylor
    series with even powers. Higher order terms don't contribute
    significantly, so a simple parabolic interpolation can generate sub-bin
    pitch accuracy.

    Args:
        y1 (float): Pitch strength at frequency bin i - 1.
        y2 (float): Pitch strength at frequency bin i.
        y3 (float): Pitch strength at frequency bin i + 1.

    Returns:
        tuple:
            vx (float): The position offset (in index) of the interpolated
                peak relative to the center index.
            vy (float): The interpolated pitch strength value at the peak.
    """
    a = (y1 - 2*y2 + y3) / 2
    b = (y3 - y1) / 2
    #c = y2

    vx = -b / (2 * a + np.finfo(np.float64).eps) # Avoids division by zero
    vy = a * vx**2 + b * vx + y2

    return vx, vy

def calcCosineKernel(f, freqList):
    """Generate a SWIPE-style kernel based on candidate frequency 'f'.

    SWIPE kernels are normalized, continuous curves generated by sums of
    positive and negative cosine lobes: positive lobes at the selected
    harmonics and negative lobes between. This SWIPE implementation uses a
    mixture of harmonics from SWIPE and SWIPE', tailored for a better match
    to human voices. The magnitude of the kernels decays as the square root
    of frequency, except for the fundamental and first harmonic, which are
    given equal weighting.

    Args:
        f (float): Fundamental frequency (in Hz).
        freqList (ndarray): Array of frequency bins for the kernel (in Hz).

    Returns:
        ndarray: Normalized kernel corresponding to the fundamental 'f'.
    """
    # Harmonics are a mix of SWIPE and SWIPE'. Good match for human voice.
    harmonics = np.array([1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 17, 19, 23])

    # Thin peaks, wide valleys
    peakWidth = 0.15
    valleyWidth = 1 - peakWidth

    valleyDivisor = 2
    decayStartHarmonic = 2

    # Kernels don't need harmonics beyond the Nyquist frequency.
    maxPossibleHarmonics = int(freqList[-1] / f)
    maxPossibleHarmonics = min(maxPossibleHarmonics, len(harmonics))
    selectedHarmonics = harmonics[:maxPossibleHarmonics]

    # For high frequencies, the kernel is normalized by the number of harmonics.
    harmonicsNormalizer = maxPossibleHarmonics / len(harmonics)

    # Normalize frequencies around the current frequency, f. Useful for harmonic comparisons.
    ratio = freqList / f

    # Initialize the kernel
    k = np.zeros_like(freqList)

    for i in np.arange(1, harmonics[-1] + 1):
        a = ratio - i # Distance from the harmonic

        # Kernels are generated from left to right around the harmonic.
        if i in selectedHarmonics:
            valleyMask = np.logical_and(-valleyWidth < a, a < -peakWidth)
            k[valleyMask] = -np.cos((a[valleyMask] + 0.5) / ((valleyWidth - peakWidth) / 2) * (np.pi / 2)) / valleyDivisor

            peakMask = np.abs(a) < peakWidth
            k[peakMask] = np.cos(a[peakMask] / peakWidth * (np.pi / 2))

        else:
            valleyMask = np.logical_and(-valleyWidth < a, a < peakWidth)
            k[valleyMask] = -np.cos((a[valleyMask] + 0.5) / ((valleyWidth - peakWidth) / 2) * (np.pi / 2)) / valleyDivisor

            peakMask = np.abs(a) < peakWidth
            k[peakMask] = np.cos(a[peakMask] / peakWidth * (np.pi / 2)) / 4

    # Piecewise decay
    decay = np.where(freqList <= f*(decayStartHarmonic + peakWidth), np.sqrt(1.0 / (f*(decayStartHarmonic + peakWidth))), np.sqrt(1.0 / freqList)) /  np.sqrt(1.0/(f*(decayStartHarmonic + peakWidth)))
    k *= decay

    # Normalize the kernel to have a positive area of 1
    k /= np.sum(k[k >0])

    # Goose kernels with fewer harmonics
    k /= harmonicsNormalizer

    return k

class PitchTracker:
    def __init__(
        self,
        input_buf: RingBuffer,
        fft_size: int = DEFAULT_FFT_SIZE,
        overlap: float = 0.75,
        sample_rate: int = SAMPLING_RATE,
        min_freq: float = DEFAULT_MIN_FREQ,
        max_freq: float = DEFAULT_MAX_FREQ,
        min_db: float = DEFAULT_MIN_DB,
        cres: int = DEFAULT_C_RES,
        conf: float = DEFAULT_P_CONF,
        p_delta: int = DEFAULT_P_DELTA
    ):
        self.fft_size = fft_size
        self.overlap = overlap
        self.sample_rate = sample_rate
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.min_db = min_db
        self.cres = cres
        self.conf = conf
        self.p_delta = p_delta
        self.prev_f0 = None

        self.input_buf = input_buf
        self.input_buf.grow_if_needed(fft_size)
        self.next_in_offset = self.input_buf.offset

        self.out_buf = RingBuffer()
        self.out_offset = self.out_buf.offset

        self.proc = audioproc()
        self.proc.set_fftsize(self.fft_size)

        # Only generate the log-spaced pitch candidates and kernels for the SWIPE algorithm on instantiation.
        self._init_swipe()

    def set_input_buffer(self, new_buf: RingBuffer) -> None:
        self.input_buf = new_buf
        self.input_buf.grow_if_needed(self.fft_size)
        self.next_in_offset = self.input_buf.offset

    def update(self) -> bool:
        new = [self.estimate_pitch(f) for f in self.new_frames()]
        self.out_buf.push(np.array([new]), 0)
        self.out_offset = self.out_buf.offset
        return len(new) != 0

    def get_estimates(self, time_s: float) -> np.ndarray:
        step_size = m.floor(self.fft_size * (1.0 - self.overlap))
        num_results = m.floor(time_s / (step_size / self.sample_rate)) + 1
        return self.out_buf.data_indexed(self.out_offset, num_results)[0,:]

    def get_latest_estimate(self) -> float:
        return self.out_buf.data_indexed(self.out_offset, 1)[0,0]

    def new_frames(self) -> Generator[np.ndarray, None, None]:
        assert self.input_buf.offset >= self.next_in_offset
        while self.next_in_offset + self.fft_size <= self.input_buf.offset:
            # data_indexed is (end_index, length) for some reason
            yield self.input_buf.data_indexed(
                self.next_in_offset + self.fft_size, self.fft_size)
            self.next_in_offset += m.floor(self.fft_size * (1.0 - self.overlap))

    def _init_swipe(self):
        """Initialize log-spaced frequency grid and SWIPE kernels.

        Constructs the log-spaced frequency grid (up to Nyquist) and the SWIPE
        kernels for frequencies up to the user selected max_freq.

        The default pitch resolution (cres) of 10 cents produces 120 pitch
        candidates per octave, which, after parabolic interpolation, is sufficient
        to generate very precise pitch estimates.
        """
        numberOfLogSpacedFreqs = int(np.log2(self.sample_rate / (2 * self.min_freq)) * (1200 / self.cres))
        self.logSpacedFreqs = np.logspace(np.log2(self.min_freq), np.log2(self.sample_rate // 2), num=numberOfLogSpacedFreqs, base=2)

        # The pitch candidates for the kernels are a subset of the log-spaced freqs only up to the user's max_freq.
        fMaxIndex = np.searchsorted(self.logSpacedFreqs, self.max_freq)
        self.pitchCandidates = self.logSpacedFreqs[:fMaxIndex]
        
        self.kernels = np.zeros((len(self.pitchCandidates), len(self.logSpacedFreqs)))
        for i, freq in enumerate(self.pitchCandidates):
            #self.kernels[i] = calcKernel(freq, self.logSpacedFreqs)
            self.kernels[i] = calcCosineKernel(freq, self.logSpacedFreqs)

    def estimate_pitch(self, frame: np.ndarray) -> Optional[float]:
        """Estimate the fundamental frequency from a single audio frame.

        Each frame's spectrum amplitude, linearly spaced, is resampled onto a
        log-spaced frequency grid and correlated against SWIPE-like kernels.
        The strongest match is refined via parabolic interpolation to achieve
        sub-bin pitch precision.

        Args:
            frame (np.ndarray): A 2D array containing one audio frame.

        Returns:
            Optional[float]: Estimated pitch in Hz, or NaN if unvoiced.
        """
        spectrum = np.abs(np.fft.rfft(frame[0, :] * self.proc.window))

        # Generate the frequency bins (linear) to that correspond with the spectrum data
        freqLin = np.arange(len(spectrum), dtype='float64')
        freqLin *= float(self.sample_rate) / float(self.fft_size)

        # Create spline mapping from linear frequency to amplitude
        # Apply this spline to the log-spaced frequencies and normalize
        specLog = np.interp(self.logSpacedFreqs, freqLin, spectrum)
        specLogRMS = np.sqrt(np.mean(specLog**2))
        specLogNorm = specLog / specLogRMS

        # Get the correlation between the audio frame and the kernels
        pitchStrengths = np.matmul(self.kernels, specLogNorm)
        
        # Get the highest strength index
        idxMax = np.argmax(pitchStrengths)

        # The highest values for pitchStrength (confidence) will come from
        # voiced pitches that nearly identically match the kernel for that
        # pitch, with a peak correlation product of around 2.56.

        # Use parabolic interp to get frequency values between resolution bins
        if 0 < idxMax < len(pitchStrengths) - 1:
            y1 = pitchStrengths[idxMax - 1]
            y2 = pitchStrengths[idxMax]
            y3 = pitchStrengths[idxMax + 1]
            idxShift, _ = fastParabolicInterp(y1, y2, y3)
        else:
            idxShift = 0

        # Generate and refine the pitch estimate by creating a mapping from indices
        # to frequency and applying it to idxMax with the interpolated index offset.
        f0 = np.interp(idxMax + idxShift, np.arange(len(self.logSpacedFreqs)), self.logSpacedFreqs)

        # Get dBFS of the frame.
        # Only signals above user's min_db threshold will be considered voiced.
        RMS = np.sqrt(np.mean(frame**2))
        dBFS = 20 * np.log10(RMS + np.finfo(np.float64).eps)

        # Exclude pitch jumps greater than p_delta semitones from the previous pitch
        if self.prev_f0 is not None and f0 != np.nan:
            semitoneDiff = 12 * np.abs(np.log2(f0 / self.prev_f0))
        else:
            semitoneDiff = 0

        # Scale the correlation strength (confidence) to be between 0 and 1
        pitchConf = pitchStrengths[idxMax] / 2.56

        # Bool conditions for unreliable pitch estimate
        pitchUnreliable = (dBFS < self.min_db) or (pitchConf < self.conf) or (semitoneDiff > self.p_delta)

        # Return
        if pitchUnreliable:
            self.prev_f0 = None
            return np.nan
        else:
            self.prev_f0 = f0
            return f0
