#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Draw and update optional reference target overlays on frequency plots."""

from __future__ import annotations

import numpy as np

from friture.reference_curves import (
    DEFAULT_REFERENCE_OFFSET_DB,
    DEFAULT_REFERENCE_PRESET,
    reference_curve_db,
    reference_overlay_label,
)


class ReferenceOverlayPlot:
    def __init__(
        self,
        plot_data,
        norm_horizontal,
        norm_vertical,
        *,
        display_mode: str,
    ) -> None:
        self._plot_data = plot_data
        self._norm_horizontal = norm_horizontal
        self._norm_vertical = norm_vertical
        self._display_mode = display_mode
        self._preset = DEFAULT_REFERENCE_PRESET
        self._offset_db = DEFAULT_REFERENCE_OFFSET_DB
        self._frequencies_hz = np.array([], dtype=float)
        self._curve = plot_data.reference_overlay

    def set_preset(self, preset: int) -> None:
        if self._preset != preset:
            self._preset = preset
            self.refresh()

    def set_offset_db(self, offset_db: float) -> None:
        offset_db = float(offset_db)
        if self._offset_db != offset_db:
            self._offset_db = offset_db
            self.refresh()

    def set_frequencies_hz(self, frequencies_hz: np.ndarray) -> None:
        self._frequencies_hz = np.asarray(frequencies_hz, dtype=float)
        self.refresh()

    def refresh(self) -> None:
        values = reference_curve_db(
            self._preset,
            self._frequencies_hz,
            offset_db=self._offset_db,
            display_mode=self._display_mode,
        )
        if values is None or self._frequencies_hz.size == 0:
            self._plot_data.set_reference_overlay_visible(False)
            return

        screen_x = self._norm_horizontal.toScreen(self._frequencies_hz)
        screen_y = 1.0 - self._norm_vertical.toScreen(values)
        self._curve.name = reference_overlay_label(self._preset, self._offset_db)
        self._curve.setData(screen_x, screen_y)
        self._plot_data.set_reference_overlay_visible(True)
