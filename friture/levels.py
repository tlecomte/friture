#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

"""Level widget that displays peak and RMS levels for 1 or 2 ports."""

from PyQt5.QtCore import QObject

from friture.levels_settings import Levels_Settings_Dialog
from friture.level_meter import LevelMeterProcessor
from friture.dock_analysis_widget import stereo_mode_from_chunk


class Levels_Widget(QObject):

    def __init__(self, parent, view_model, global_calibration) -> None:
        super().__init__(parent)

        self._parent = parent
        self.level_view_model = view_model
        self._global_calibration = global_calibration
        self.audiobuffer = None
        self.settings_dialog = Levels_Settings_Dialog(parent)
        self._meter = LevelMeterProcessor()
        self._global_calibration.changed.connect(self._sync_unit_label)
        self._sync_unit_label()

    @property
    def last_raw_rms_db(self) -> float:
        return self._meter.last_raw_rms_db

    def _sync_unit_label(self) -> None:
        self.level_view_model.unit_label = self._global_calibration.calibration.unit_label

    def set_buffer(self, buffer) -> None:
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata) -> None:
        self._meter.handle_new_data(
            floatdata,
            self.level_view_model,
            self._global_calibration.calibration,
        )

    def canvasUpdate(self) -> None:
        if not self._parent.isVisible():
            return
        self._meter.canvas_update(self.level_view_model, True)

    def settings_called(self, checked) -> None:
        self.settings_dialog.show()

    def saveState(self, settings) -> None:
        self.settings_dialog.saveState(settings)

    def restoreState(self, settings) -> None:
        self.settings_dialog.restoreState(settings)
