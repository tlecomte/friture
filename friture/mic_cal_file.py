#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Parse microphone calibration files (factory .txt and REW-style .cal)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

import numpy as np

_FACTORY_HEADER_RE = re.compile(
    r"^\*\s*(?P<freq>[\d.]+)\s*Hz\s+(?P<sens>-?[\d.]+)\s*$",
    re.IGNORECASE,
)
_SENSITIVITY_DBFS_RE = re.compile(
    r"^Sensitivity\s+(?P<sens>-?[\d.]+)\s*dBFS\s*$",
    re.IGNORECASE,
)
_SENS_FACTOR_RE = re.compile(
    r"^Sens\s+Factor\s*=\s*(?P<sens>-?[\d.]+)\s*dB",
    re.IGNORECASE,
)
_DATA_LINE_RE = re.compile(
    r"^\s*(?P<freq>[\d.]+)\s*[, \t]\s*(?P<gain>-?[\d.]+)(?:\s*[, \t]\s*[-\d.]+)?\s*(?:$|[\t,])"
)


class MicCalFileError(ValueError):
    pass


@dataclass(frozen=True)
class MicCalFile:
    frequencies_hz: np.ndarray
    corrections_db: np.ndarray
    sensitivity_db: float | None = None
    reference_freq_hz: float | None = None
    source_path: str = ""

    @property
    def has_frequency_data(self) -> bool:
        return len(self.frequencies_hz) >= 2

    def interpolate_db(self, frequencies_hz: np.ndarray) -> np.ndarray:
        if not self.has_frequency_data:
            return np.zeros_like(frequencies_hz, dtype=float)

        freqs = np.asarray(frequencies_hz, dtype=float)
        cal_freq = self.frequencies_hz
        cal_corr = self.corrections_db
        log_cal = np.log10(cal_freq)
        log_freq = np.log10(np.clip(freqs, cal_freq[0], cal_freq[-1]))
        return np.interp(log_freq, log_cal, cal_corr)

    def summary(self) -> str:
        parts: list[str] = []
        if self.source_path:
            parts.append(os.path.basename(self.source_path))
        if self.sensitivity_db is not None:
            ref = (
                f" @ {self.reference_freq_hz:g} Hz"
                if self.reference_freq_hz is not None
                else ""
            )
            parts.append(f"sensitivity {self.sensitivity_db:.1f} dB{ref}")
        if self.has_frequency_data:
            parts.append(f"{len(self.frequencies_hz)} frequency points")
        return ", ".join(parts) if parts else "Empty calibration file"

    @classmethod
    def parse_text(cls, text: str, source_path: str = "") -> MicCalFile:
        sensitivity_db: float | None = None
        reference_freq_hz: float | None = None
        frequencies: list[float] = []
        corrections: list[float] = []

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            factory_match = _FACTORY_HEADER_RE.match(stripped)
            if factory_match:
                reference_freq_hz = float(factory_match.group("freq"))
                sensitivity_db = float(factory_match.group("sens"))
                continue

            sensitivity_match = _SENSITIVITY_DBFS_RE.match(stripped)
            if sensitivity_match:
                sensitivity_db = float(sensitivity_match.group("sens"))
                continue

            sens_factor_match = _SENS_FACTOR_RE.match(stripped)
            if sens_factor_match:
                sensitivity_db = float(sens_factor_match.group("sens"))
                continue

            data_match = _DATA_LINE_RE.match(stripped)
            if not data_match:
                continue

            freq = float(data_match.group("freq"))
            gain = float(data_match.group("gain"))
            if frequencies and freq <= frequencies[-1]:
                raise MicCalFileError(
                    f"Frequencies must increase (got {freq} after {frequencies[-1]})"
                )
            frequencies.append(freq)
            corrections.append(gain)

        if len(frequencies) < 2:
            raise MicCalFileError("Calibration file must contain at least two frequency points")

        return cls(
            frequencies_hz=np.asarray(frequencies, dtype=float),
            corrections_db=np.asarray(corrections, dtype=float),
            sensitivity_db=sensitivity_db,
            reference_freq_hz=reference_freq_hz,
            source_path=source_path,
        )


def load_mic_cal_file(path: str) -> MicCalFile:
    with open(path, encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    return MicCalFile.parse_text(text, source_path=os.path.abspath(path))
