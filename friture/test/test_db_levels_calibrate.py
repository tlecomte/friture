# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Tests for quick-calibrate button on the dB Levels dock."""

import unittest
from unittest.mock import MagicMock, patch

from friture.test.helpers import (
    AudioHarness,
    attach_global_calibration,
    ensure_qapplication,
    make_parent_widget,
)


class DbLevelsDockCalibrateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ensure_qapplication()

    def setUp(self) -> None:
        self.parent = make_parent_widget()
        attach_global_calibration(self.parent)
        from friture.db_levels_dock import DbLevelsDockWidget
        self.widget = DbLevelsDockWidget(self.parent)
        self.harness = AudioHarness()
        self.widget.set_buffer(self.harness.buffer)

    def test_dock_exposes_calibrate_global_method(self) -> None:
        self.assertTrue(callable(getattr(self.widget, "calibrate_global", None)))

    def test_calibrate_global_calls_calibrate_interactive(self) -> None:
        self.harness.push_sine(440.0, 4096, amplitude=0.5)

        with patch("friture.db_levels_dock.calibrate_interactive") as mock_fn:
            self.widget.calibrate_global()

        mock_fn.assert_called_once()
        _, cal_arg, parent_arg = mock_fn.call_args[0]
        self.assertIs(cal_arg, self.parent.global_calibration)

    def test_calibrate_global_no_op_when_no_global_calibration(self) -> None:
        parent = make_parent_widget()  # no global_calibration attached
        from friture.db_levels_dock import DbLevelsDockWidget
        widget = DbLevelsDockWidget(parent)

        with patch("friture.db_levels_dock.calibrate_interactive") as mock_fn:
            widget.calibrate_global()

        mock_fn.assert_not_called()
