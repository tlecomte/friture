#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Wire global scalar calibration to frequency-widget display ranges."""

from __future__ import annotations

from friture.global_frequency_calibration import calibrated_spec_range
from friture.level_calibration import find_global_calibration


class CalibratedDisplayRangeMixin:
    """Keep user spec min/max in base_*; shift plot range by global offset."""

    _calibration_owner = None
    _base_spec_min: float = 0.0
    _base_spec_max: float = 0.0

    def init_calibrated_display_range(
        self, owner, base_min: float, base_max: float
    ) -> None:
        self._calibration_owner = owner
        self._base_spec_min = base_min
        self._base_spec_max = base_max
        service = find_global_calibration(owner)
        if service is not None:
            service.changed.connect(self._sync_calibrated_display_range)
        self._sync_calibrated_display_range()

    def set_base_spec_min(self, value: float) -> None:
        self._base_spec_min = value
        self._sync_calibrated_display_range()

    def set_base_spec_max(self, value: float) -> None:
        self._base_spec_max = value
        self._sync_calibrated_display_range()

    def _sync_calibrated_display_range(self) -> None:
        self.spec_min, self.spec_max = calibrated_spec_range(
            self._base_spec_min,
            self._base_spec_max,
            self._calibration_owner,
        )
        self._apply_calibrated_spec_range(self.spec_min, self.spec_max)

    def _apply_calibrated_spec_range(self, spec_min: float, spec_max: float) -> None:
        raise NotImplementedError
