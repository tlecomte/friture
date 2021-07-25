#!/bin/bash

set -x

which python3
python3 -c 'import sys; print(sys.version)'

pip3 install -r requirements.txt

# pyinstaller needs to have the extensions built explicitely
python3 setup.py build_ext --inplace

# for Macos Big Sur, the stable portaudio (19.6.0) makes Friture freeze on startup
# install from latest master instead
# see: https://github.com/tlecomte/friture/issues/154
brew install portaudio --HEAD

pip3 install -U pyinstaller==4.4

pyinstaller friture.spec -y --onedir --windowed

ls -la dist/*

# compare the portaudio libs to make sure the package contains the one that was installed with brew
ls -la /usr/local/lib/libportaudio.dylib
ls -la /usr/local/Cellar/portaudio/*/lib/libportaudio*.dylib
ls -la dist/friture.app/Contents/MacOS/_sounddevice_data/portaudio-binaries

# prepare a dmg out of friture.app
export ARTIFACT_FILENAME=friture-$(python3 -c 'import friture; print(friture.__version__)')-$(date +'%Y%m%d').dmg
echo $ARTIFACT_FILENAME
hdiutil create $ARTIFACT_FILENAME -volname "Friture" -fs HFS+ -srcfolder dist/friture.app
du -hs dist/friture.app
du -hs $ARTIFACT_FILENAME