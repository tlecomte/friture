#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Pure-numpy spectrum analysis for dock widgets (no Qt)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np
from numpy import arange, argmax, float64, log10, ones, zeros

from friture.audiobackend import SAMPLING_RATE
from friture.audioproc import audioproc
from friture.spectrum_settings import (
    DEFAULT_MAXFREQ,
    DEFAULT_MINFREQ,
    DEFAULT_RESPONSE_TIME,
    DEFAULT_WEIGHTING,
)
from friture_extensions.exp_smoothing_conv import pyx_exp_smoothed_value_numpy


@dataclass(frozen=True)
class SpectrumFrameResult:
    freq: np.ndarray
    db_spectrogram: np.ndarray
    fmax_hz: float
    fpitch_hz: float


class SpectrumFrameAnalyzer:
    """FFT spectrum + smoothing + peak pick from ring-buffer frames."""

    def __init__(
        self,
        fft_size: int,
        overlap: float = 0.75,
        minfreq: float = DEFAULT_MINFREQ,
        maxfreq: float = DEFAULT_MAXFREQ,
        weighting: int = DEFAULT_WEIGHTING,
        response_time: float = DEFAULT_RESPONSE_TIME,
        dual_channels: bool = False,
    ) -> None:
        self.overlap = overlap
        self.fft_size = fft_size
        self.minfreq = minfreq
        self.maxfreq = maxfreq
        self.weighting = weighting
        self.response_time = response_time
        self.dual_channels = dual_channels

        self._proc = audioproc()
        self._proc.set_maxfreq(max(self.minfreq, self.maxfreq))
        self._proc.set_fftsize(self.fft_size)

        self.freq = self._proc.get_freq_scale()
        self._w = zeros(self.freq.shape)
        self._update_weighting()

        self._dispbuffers1 = zeros(len(self.freq))
        self._dispbuffers2 = zeros(len(self.freq))
        self._set_response_time(self.response_time)

    @property
    def proc(self) -> audioproc:
        return self._proc

    def set_fft_size(self, fft_size: int) -> None:
        self.fft_size = fft_size
        self._proc.set_fftsize(fft_size)
        self.freq = self._proc.get_freq_scale()
        self._reset_display_buffers()
        self._update_weighting()
        self._set_response_time(self.response_time)

    def set_freq_range(self, minfreq: float, maxfreq: float) -> None:
        self.minfreq = minfreq
        self.maxfreq = maxfreq
        self._proc.set_maxfreq(max(minfreq, maxfreq))
        self.freq = self._proc.get_freq_scale()
        self._reset_display_buffers()
        self._update_weighting()
        self._set_response_time(self.response_time)

    def set_weighting(self, weighting: int) -> None:
        self.weighting = weighting
        self._update_weighting()

    def set_response_time(self, response_time: float) -> None:
        self.response_time = response_time
        self._set_response_time(response_time)

    def set_dual_channels(self, dual_channels: bool) -> None:
        self.dual_channels = dual_channels

    def process_frames(
        self, frames: Sequence[np.ndarray]
    ) -> Optional[SpectrumFrameResult]:
        realizable = len(frames)
        if realizable == 0:
            return None

        sp1n = zeros((len(self.freq), realizable), dtype=float64)
        sp2n = zeros((len(self.freq), realizable), dtype=float64)

        last_frame = frames[-1]
        for i, frame in enumerate(frames):
            sp1n[:, i] = self._proc.analyzelive(frame[0, :])
            if self.dual_channels and frame.shape[0] > 1:
                sp2n[:, i] = self._proc.analyzelive(frame[1, :])

        sp1 = pyx_exp_smoothed_value_numpy(
            self._kernel, self._alpha, sp1n, self._dispbuffers1
        )
        sp2 = pyx_exp_smoothed_value_numpy(
            self._kernel, self._alpha, sp2n, self._dispbuffers2
        )
        self._dispbuffers1 = sp1
        self._dispbuffers2 = sp2

        sp1.shape = self.freq.shape
        sp2.shape = self.freq.shape
        w = self._w.reshape(self.freq.shape)

        if self.dual_channels and last_frame.shape[0] > 1:
            db_spectrogram = self._log_spectrogram(sp2) - self._log_spectrogram(sp1)
        else:
            db_spectrogram = self._log_spectrogram(sp1) + w

        peak_index = argmax(db_spectrogram)
        fmax_hz = float(self.freq[peak_index])

        harmonic_products = self._harmonic_product_spectrum(sp1)
        pitch_idx = argmax(harmonic_products)
        fpitch_hz = float(max(self.freq[pitch_idx], 1e-20))

        return SpectrumFrameResult(
            freq=self.freq,
            db_spectrogram=db_spectrogram,
            fmax_hz=fmax_hz,
            fpitch_hz=fpitch_hz,
        )

    def _reset_display_buffers(self) -> None:
        self._dispbuffers1 = zeros(len(self.freq))
        self._dispbuffers2 = zeros(len(self.freq))

    def _set_response_time(self, response_time: float) -> None:
        w = 0.65
        delta_n = self.fft_size * (1.0 - self.overlap)
        n = response_time * SAMPLING_RATE / delta_n
        n_kernel = 2 * 4096
        self._alpha = 1.0 - (1.0 - w) ** (1.0 / (n + 1))
        self._kernel = (1.0 - self._alpha) ** arange(n_kernel - 1, -1, -1)

    def _update_weighting(self) -> None:
        a_weight, b_weight, c_weight = self._proc.get_freq_weighting()
        if self.weighting == 0:
            self._w = zeros(a_weight.shape)
        elif self.weighting == 1:
            self._w = a_weight
        elif self.weighting == 2:
            self._w = b_weight
        else:
            self._w = c_weight

    @staticmethod
    def _log_spectrogram(sp: np.ndarray) -> np.ndarray:
        epsilon = 1e-30
        return 10.0 * log10(sp + epsilon)

    @staticmethod
    def _harmonic_product_spectrum(sp: np.ndarray) -> np.ndarray:
        product_count = 3
        harmonic_length = sp.shape[0] // product_count

        if product_count == 3:
            return (
                sp[:harmonic_length]
                * sp[::2][:harmonic_length]
                * sp[::3][:harmonic_length]
            )

        res = ones(harmonic_length, dtype=sp.dtype)
        for i in range(1, product_count + 1):
            res *= sp[::i][:harmonic_length]
        return res
