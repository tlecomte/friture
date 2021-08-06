# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------
# -----------------------------------------------------------------------------

"""
sounddevice:
https://github.com/spatialaudio/python-sounddevice/
"""

import os

from PyInstaller.compat import is_darwin, is_win
from PyInstaller.utils.hooks import get_package_paths

sfp = get_package_paths("sounddevice")

path = None
if is_win:
    path = os.path.join(sfp[0], "_sounddevice_data", "portaudio-binaries")
elif is_darwin:
    # for Macos Big Sur, the stable portaudio (19.6.0) makes Friture freeze on startup
    path = "/usr/local/lib/libportaudio.dylib"
    if not os.path.isfile(path):
        raise ValueError('libportaudio could not be found')

if path is not None and os.path.exists(path):
    binaries = [(path,
                 os.path.join("_sounddevice_data", "portaudio-binaries"))]
