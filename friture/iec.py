#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2021 Timothée Lecomte

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

def dB_to_IEC(dB):
    if dB < -70.0:
        return 0.0
    elif dB < -60.0:
        return (dB + 70.0) * 0.0025
    elif dB < -50.0:
        return (dB + 60.0) * 0.005 + 0.025
    elif dB < -40.0:
        return (dB + 50.0) * 0.0075 + 0.075
    elif dB < -30.0:
        return (dB + 40.0) * 0.015 + 0.15
    elif dB < -20.0:
        return (dB + 30.0) * 0.02 + 0.3
    else:
        return min(1.0, (dB + 20.0) * 0.025 + 0.5)


# Meter bar shows readings between bottom and top (calibrated dB values).
# dB FS keeps the classic IEC scale on raw digital levels instead of a linear range.
METER_DISPLAY_RANGE = {
    "dBSPL": (40.0, 120.0),
    "dBu": (-40.0, 20.0),
}

DIGITAL_UNIT_LABELS = frozenset({"dB FS", "dBFS", "dB"})


def normalize_unit_label(unit_label: str) -> str:
    if unit_label in ("dBFS", "dB"):
        return "dB FS"
    return unit_label


def meter_display_range(unit_label: str) -> tuple[float, float] | None:
    return METER_DISPLAY_RANGE.get(normalize_unit_label(unit_label))


def uses_iec_meter_scale(unit_label: str) -> bool:
    return meter_display_range(unit_label) is None


def meter_level_for_bar(
    display_db: float, raw_db: float, unit_label: str = "dB FS"
) -> float:
    """Pick the dB value that drives the meter bar for a unit."""
    if uses_iec_meter_scale(unit_label):
        return raw_db
    return display_db


def meter_scale_ticks(unit_label: str) -> list[float]:
    normalized = normalize_unit_label(unit_label)
    display_range = meter_display_range(normalized)
    if display_range is None:
        return [0.0, -3.0, -6.0, -10.0, -20.0, -30.0, -40.0, -50.0, -60.0]
    bottom, top = display_range
    step = 10.0 if normalized == "dBSPL" else 10.0
    ticks: list[float] = []
    tick = top
    while tick >= bottom:
        ticks.append(tick)
        tick -= step
    return ticks


def level_db_to_meter_fraction(level_db: float, unit_label: str = "dB FS") -> float:
    """Map a level reading to a 0..1 meter bar height."""
    normalized = normalize_unit_label(unit_label)
    display_range = meter_display_range(normalized)
    if display_range is None:
        return dB_to_IEC(min(level_db, 0.0))

    bottom, top = display_range
    if level_db <= bottom:
        return 0.0
    if level_db >= top:
        return 1.0
    return (level_db - bottom) / (top - bottom)


def level_db_to_iec(level_db: float, unit_label: str = "dB FS") -> float:
    """Backward-compatible alias for meter bar height."""
    return level_db_to_meter_fraction(level_db, unit_label)


def iec_to_dB(iec):
    if iec <= 0.0:
        return -70.0
    if iec <= 0.025:
        return iec / 0.0025 - 70.0
    if iec <= 0.075:
        return (iec - 0.025) / 0.005 - 60.0
    if iec <= 0.15:
        return (iec - 0.075) / 0.0075 - 50.0
    if iec <= 0.3:
        return (iec - 0.15) / 0.015 - 40.0
    if iec <= 0.5:
        return (iec - 0.3) / 0.02 - 30.0
    return (iec - 0.5) / 0.025 - 20.0