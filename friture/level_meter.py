#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Shared peak/RMS level meter math for sidebar and dock widgets."""

from __future__ import annotations

import numpy as np

from friture.audiobackend import SAMPLING_RATE
from friture.dock_analysis_widget import stereo_mode_from_chunk
from friture.iec import level_db_to_meter_fraction, meter_level_for_bar
from friture.freq_weighting import DEFAULT_WEIGHTING, WeightingFilter
from friture.level_calibration import LevelCalibration, apply_calibration
from friture.level_view_model import LevelViewModel
from friture_extensions.exp_smoothing_conv import pyx_exp_smoothed_value

DEFAULT_RESPONSE_TIME_S = 0.300
DEFAULT_PEAK_RESPONSE_TIME_S = 0.025
SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
LEVEL_TEXT_LABEL_PERIOD_MS = 250
LEVEL_TEXT_LABEL_STEPS = LEVEL_TEXT_LABEL_PERIOD_MS / SMOOTH_DISPLAY_TIMER_PERIOD_MS


def _smoothing_kernel(response_time_s: float) -> tuple[float, np.ndarray]:
    w = 0.65
    n = response_time_s * SAMPLING_RATE
    n_samples = int(5 * n)
    alpha = 1.0 - (1.0 - w) ** (1.0 / (n + 1))
    kernel = (1.0 - alpha) ** (np.arange(0, n_samples)[::-1])
    return alpha, kernel


def _peak_alpha(response_time_s: float = DEFAULT_PEAK_RESPONSE_TIME_S) -> float:
    w = 0.65
    n2 = response_time_s / (SMOOTH_DISPLAY_TIMER_PERIOD_MS / 1000.0)
    return 1.0 - (1.0 - w) ** (1.0 / (n2 + 1))


class LevelMeterProcessor:
    def __init__(
        self,
        response_time_s: float = DEFAULT_RESPONSE_TIME_S,
        peak_response_time_s: float = DEFAULT_PEAK_RESPONSE_TIME_S,
    ) -> None:
        self.response_time_s = response_time_s
        self.peak_response_time_s = peak_response_time_s
        self._alpha, self._kernel = _smoothing_kernel(response_time_s)
        self._alpha2 = _peak_alpha(peak_response_time_s)
        self._old_rms = 1e-30
        self._old_max = 1e-30
        self._old_rms_2 = 1e-30
        self._old_max_2 = 1e-30
        self.two_channels = False
        self._canvas_step = 0
        self.last_raw_rms_db = -120.0
        self._weighting_filter = WeightingFilter()

    def set_weighting(self, weighting: int) -> None:
        self._weighting_filter.set_weighting(weighting)

    def weighting(self) -> int:
        return self._weighting_filter.weighting

    def set_response_time_s(self, response_time_s: float) -> None:
        self.response_time_s = response_time_s
        self._alpha, self._kernel = _smoothing_kernel(response_time_s)

    def reset_smoothing(self) -> None:
        self._old_rms = 1e-30
        self._old_max = 1e-30
        self._old_rms_2 = 1e-30
        self._old_max_2 = 1e-30
        self.last_raw_rms_db = -120.0

    def handle_new_data(
        self,
        floatdata: np.ndarray,
        view_model: LevelViewModel,
        calibration: LevelCalibration,
    ) -> None:
        updated = stereo_mode_from_chunk(floatdata, self.two_channels)
        if updated != self.two_channels:
            self.two_channels = updated
            view_model.two_channels = updated

        y1 = floatdata[0, :]
        y1 = self._weighting_filter.apply(y1, channel=1)
        raw_rms_db, raw_max_db = self._channel_raw_db(y1, channel=1)
        self.last_raw_rms_db = raw_rms_db
        self._apply_channel(
            raw_rms_db,
            raw_max_db,
            view_model.level_data,
            view_model.level_data_ballistic,
            calibration,
        )

        if self.two_channels:
            y2 = floatdata[1, :]
            y2 = self._weighting_filter.apply(y2, channel=2)
            raw_rms_db_2, raw_max_db_2 = self._channel_raw_db(y2, channel=2)
            self._apply_channel(
                raw_rms_db_2,
                raw_max_db_2,
                view_model.level_data_2,
                view_model.level_data_ballistic_2,
                calibration,
            )

    def _channel_raw_db(
        self, samples: np.ndarray, channel: int
    ) -> tuple[float, float]:
        old_max = self._old_max if channel == 1 else self._old_max_2
        old_rms = self._old_rms if channel == 1 else self._old_rms_2

        if len(samples) > 0:
            value_max = np.abs(samples).max()
            if value_max > old_max * (1.0 - self._alpha2):
                old_max = value_max
            else:
                old_max *= 1.0 - self._alpha2

        value_rms = pyx_exp_smoothed_value(
            self._kernel, self._alpha, samples**2, old_rms
        )

        if channel == 1:
            self._old_max = old_max
            self._old_rms = value_rms
        else:
            self._old_max_2 = old_max
            self._old_rms_2 = value_rms

        raw_rms_db = 10.0 * np.log10(value_rms + 1e-80)
        raw_max_db = 20.0 * np.log10(old_max + 1e-80)
        return raw_rms_db, raw_max_db

    def _apply_channel(
        self,
        raw_rms_db: float,
        raw_max_db: float,
        level_data,
        ballistic,
        calibration: LevelCalibration,
    ) -> None:
        level_data.level_rms_raw = raw_rms_db
        level_data.level_max_raw = raw_max_db
        level_data.level_rms = apply_calibration(raw_rms_db, calibration.offset_db)
        level_data.level_max = apply_calibration(raw_max_db, calibration.offset_db)
        meter_rms_db = meter_level_for_bar(
            level_data.level_rms, raw_rms_db, calibration.unit_label
        )
        meter_max_db = meter_level_for_bar(
            level_data.level_max, raw_max_db, calibration.unit_label
        )
        peak_db = max(meter_max_db, meter_rms_db)
        ballistic.peak_iec = level_db_to_meter_fraction(
            peak_db, calibration.unit_label
        )

    def canvas_update(self, view_model: LevelViewModel, parent_visible: bool) -> None:
        if not parent_visible:
            return

        self._canvas_step += 1
        if self._canvas_step == LEVEL_TEXT_LABEL_STEPS:
            view_model.level_data_slow.level_rms = view_model.level_data.level_rms
            view_model.level_data_slow.level_max = view_model.level_data.level_max
            if self.two_channels:
                view_model.level_data_slow_2.level_rms = (
                    view_model.level_data_2.level_rms
                )
                view_model.level_data_slow_2.level_max = (
                    view_model.level_data_2.level_max
                )
        self._canvas_step %= LEVEL_TEXT_LABEL_STEPS


MIN_CALIBRATION_RAW_DB = -90.0
DEFAULT_CALIBRATION_WINDOW_SAMPLES = 4096


def measure_raw_rms_db(
    samples: np.ndarray,
    *,
    weighting: int = DEFAULT_WEIGHTING,
) -> float:
    if samples.size == 0:
        return -120.0
    weighting_filter = WeightingFilter()
    weighting_filter.set_weighting(weighting)
    weighted = weighting_filter.apply(np.asarray(samples, dtype=float), channel=1)
    mean_square = float(np.mean(weighted * weighted))
    return float(10.0 * np.log10(mean_square + 1e-80))


def raw_rms_db_from_buffer(
    buffer,
    *,
    num_samples: int = DEFAULT_CALIBRATION_WINDOW_SAMPLES,
    weighting: int = DEFAULT_WEIGHTING,
) -> float:
    if buffer is None:
        return -120.0

    available = buffer.ringbuffer.offset
    if available <= 0:
        return -120.0

    length = min(num_samples, available)
    data = buffer.data(length)
    if data.shape[1] == 0:
        return -120.0

    return max(
        measure_raw_rms_db(data[channel], weighting=weighting)
        for channel in range(data.shape[0])
    )


def calibration_signal_too_quiet(raw_rms_db: float) -> bool:
    return raw_rms_db <= MIN_CALIBRATION_RAW_DB


def calibration_raw_rms_db(
    buffer,
    *,
    live_raw_rms_db: float | None = None,
    meter: LevelMeterProcessor | None = None,
    num_samples: int = DEFAULT_CALIBRATION_WINDOW_SAMPLES,
    weighting: int = DEFAULT_WEIGHTING,
) -> float:
    """Best current raw RMS for calibration: buffer window or live meter, whichever is louder."""
    from_buffer = raw_rms_db_from_buffer(
        buffer,
        num_samples=num_samples,
        weighting=weighting,
    )
    if meter is not None:
        live_raw_rms_db = meter.last_raw_rms_db
    if live_raw_rms_db is None:
        return from_buffer
    return max(from_buffer, live_raw_rms_db)


def calibration_quiet_message(
    raw_rms_db: float,
    *,
    offset_db: float = 0.0,
    unit_label: str = "dB FS",
) -> str:
    lines = [
        "No usable input signal for calibration.",
        "",
        f"Current raw level is {raw_rms_db:.1f} dBFS.",
    ]
    if abs(offset_db) > 0.1:
        apparent_db = raw_rms_db + offset_db
        lines.extend(
            [
                f"Current calibration offset is {offset_db:.1f} dB ({unit_label}).",
                f"Meters and graphs may show about {apparent_db:.1f} {unit_label}, "
                "but that comes from the offset—not from input level.",
                "",
                "Reset the offset to 0 if no calibrator is connected, then calibrate "
                "again once a reference tone is present (typically above -60 dBFS raw).",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "Apply a calibrator or test tone (typically above -60 dBFS raw), "
                "then try again.",
            ]
        )
    return "\n".join(lines)

