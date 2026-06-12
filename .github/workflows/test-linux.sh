#!/bin/bash

set -euxo pipefail

export QT_QPA_PLATFORM=offscreen
export QT_QUICK_CONTROLS_STYLE=Fusion

python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"

python3 setup.py build_ext --inplace

python3 -m coverage run --source=friture friture/test/runner.py
python3 -m coverage report --fail-under=16
