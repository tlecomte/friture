#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Celeste Sinéad

"""Input device catalog seam — query/select capture hardware without settings UI."""

from __future__ import annotations

import re
import sys
from typing import Protocol, runtime_checkable

from PyQt5 import QtCore, QtWidgets

from friture.audio_ingest import get_audio_ingest

NO_INPUT_DEVICE_TITLE = "No audio input device found"

NO_INPUT_DEVICE_MESSAGE = """No audio input device has been found.

Friture needs at least one input device. Please check your audio configuration.

Friture will now exit.
"""


@runtime_checkable
class InputDeviceCatalog(Protocol):
    """Device listing and selection surface shared by ingest adapters."""

    def get_readable_devices_list(self) -> list[str]:
        ...

    def get_readable_current_channels(self) -> list[str]:
        ...

    def get_readable_current_device(self) -> int:
        ...

    def get_current_first_channel(self) -> int:
        ...

    def get_current_second_channel(self) -> int:
        ...

    def select_input_device(self, index: int) -> tuple[bool, int]:
        ...

    def select_first_channel(self, index: int) -> tuple[bool, int]:
        ...

    def select_second_channel(self, index: int) -> tuple[bool, int]:
        ...

    def set_single_input(self) -> None:
        ...

    def set_duo_input(self) -> None:
        ...

    def get_current_device_key(self) -> str:
        ...


def sanitize_device_key(name: str, host_api: str) -> str:
    """Return a QSettings-safe composite key for a device identity."""
    safe_name = re.sub(r"[^A-Za-z0-9_\-]", "_", name) if name else "__unknown__"
    safe_api = re.sub(r"[^A-Za-z0-9_\-]", "_", host_api)
    return f"{safe_name}__{safe_api}"


def compute_device_key(device: dict) -> str:
    """Return sanitized composite key for a sounddevice device dict. Empty on error."""
    try:
        import sounddevice
        host_api_name = sounddevice.query_hostapis(device["hostapi"])["name"]
        return sanitize_device_key(device["name"], host_api_name)
    except Exception:
        return ""


def get_input_device_catalog() -> InputDeviceCatalog:
    return get_audio_ingest()  # type: ignore[return-value]


def require_input_devices(
    parent: QtWidgets.QWidget | None, catalog: InputDeviceCatalog
) -> None:
    """Production policy: quit when capture is required but no inputs exist."""
    if catalog.get_readable_devices_list():
        return

    QtWidgets.QMessageBox.critical(
        parent, NO_INPUT_DEVICE_TITLE, NO_INPUT_DEVICE_MESSAGE
    )
    app = QtWidgets.QApplication.instance()
    if app is not None:
        QtCore.QTimer.singleShot(0, app.quit)
    sys.exit(1)


def apply_saved_input_selection(
    catalog: InputDeviceCatalog,
    device_name: str,
    first_channel: int,
    second_channel: int,
    duo_input: bool,
) -> bool:
    """Activate the last-used input device on the catalog. Returns False if unknown."""
    devices = catalog.get_readable_devices_list()
    if device_name not in devices:
        return False

    device_index = devices.index(device_name)
    success, device_index = catalog.select_input_device(device_index)
    if not success:
        return False

    catalog.select_first_channel(first_channel)
    catalog.select_second_channel(second_channel)
    if duo_input:
        catalog.set_duo_input()
    else:
        catalog.set_single_input()
    return True
