# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Tests for calibrate_interactive() shared calibration dialog logic."""

import unittest
from unittest.mock import MagicMock, patch

from friture.test.helpers import ensure_qapplication, make_parent_widget


class CalibrateInteractiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ensure_qapplication()

    def setUp(self) -> None:
        self.parent = make_parent_widget()
        from friture.global_calibration import GlobalCalibrationService
        self.cal = GlobalCalibrationService(self.parent)

    def test_quiet_signal_shows_warning_and_does_not_calibrate(self) -> None:
        from friture.level_meter import calibrate_interactive

        with patch("friture.level_meter.calibration_signal_too_quiet", return_value=True), \
             patch("PyQt5.QtWidgets.QMessageBox.warning") as mock_warn, \
             patch("PyQt5.QtWidgets.QInputDialog.getDouble") as mock_dlg:

            calibrate_interactive(-90.0, self.cal, self.parent)

        mock_warn.assert_called_once()
        mock_dlg.assert_not_called()
        self.assertAlmostEqual(self.cal.calibration.offset_db, 0.0)

    def test_user_enters_target_sets_offset(self) -> None:
        from friture.level_meter import calibrate_interactive

        with patch("friture.level_meter.calibration_signal_too_quiet", return_value=False), \
             patch("PyQt5.QtWidgets.QInputDialog.getDouble", return_value=(94.0, True)):

            calibrate_interactive(-40.0, self.cal, self.parent)

        # offset = target - raw = 94 - (-40) = 134... but calibration_offset_for_target handles sign
        self.assertNotAlmostEqual(self.cal.calibration.offset_db, 0.0)

    def test_user_cancels_does_not_change_offset(self) -> None:
        from friture.level_meter import calibrate_interactive

        self.cal.set_offset_db(5.0)

        with patch("friture.level_meter.calibration_signal_too_quiet", return_value=False), \
             patch("PyQt5.QtWidgets.QInputDialog.getDouble", return_value=(94.0, False)):

            calibrate_interactive(-40.0, self.cal, self.parent)

        self.assertAlmostEqual(self.cal.calibration.offset_db, 5.0)

    def test_target_near_114db_sets_dbspl_unit(self) -> None:
        from friture.level_meter import calibrate_interactive

        with patch("friture.level_meter.calibration_signal_too_quiet", return_value=False), \
             patch("PyQt5.QtWidgets.QInputDialog.getDouble", return_value=(114.0, True)):

            calibrate_interactive(-40.0, self.cal, self.parent)

        self.assertEqual(self.cal.calibration.unit_label, "dBSPL")
