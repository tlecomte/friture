#!/bin/bash

set -x

which python3
python3 -c 'import sys; print(sys.version)'

pip3 install -r requirements.txt

# pyinstaller needs to have the extensions built explicitely
python3 setup.py build_ext --inplace

pip3 install -U pyinstaller==4.2

pyinstaller friture.spec -y --onedir --windowed

ls -la dist/*

# prepare a dmg out of friture.app
export ARTIFACT_FILENAME=friture-$(python3 -c 'import friture; print(friture.__version__)')-$(date +'%Y%m%d').dmg
echo $ARTIFACT_FILENAME
hdiutil create $ARTIFACT_FILENAME -volname "Friture" -fs HFS+ -srcfolder dist/friture.app
du -hs dist/friture.app
du -hs $ARTIFACT_FILENAME