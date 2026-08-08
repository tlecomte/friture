#!/bin/bash

set -x

uv run python -c 'import sys; print(sys.version)'

# For macOS Big Sur, the stable portaudio (19.6.0) makes Friture freeze on startup
# install from a newer master commit instead
# see: https://github.com/tlecomte/friture/issues/154
PORTAUDIO_COMMIT=aa7a7902f1b79502633aeb88919657af46c84193
rm -rf build/portaudio
git clone https://github.com/PortAudio/portaudio.git build/portaudio
cd build/portaudio
git checkout $PORTAUDIO_COMMIT
./configure --enable-mac-universal=no --enable-cxx
make
sudo make install
cd -

uv run pyinstaller friture.spec -y

ls -la dist/*

# compare the portaudio libs to make sure the package contains the one that was installed with brew
ls -la /usr/local/lib/libportaudio.dylib
ls -la dist/friture.app/Contents/Frameworks/_sounddevice_data/portaudio-binaries

# PyInstaller will try to codesign friture.app, but will fail because of the Qt5 file structure
# (this is visible in the logs)
# see https://github.com/pyinstaller/pyinstaller/wiki/Recipe-OSX-Code-Signing-Qt
# so we fix the folder names and then sign again manually
uv run python installer/fix_app_qt_folder_names_for_codesign.py dist/friture.app
codesign -s - --force --all-architectures --timestamp --deep dist/friture.app
codesign -dv dist/friture.app

# prepare a dmg out of friture.app
export ARTIFACT_FILENAME=friture-$(uv run python -c 'import friture; print(friture.__version__)')-$(date +'%Y%m%d').dmg
echo $ARTIFACT_FILENAME

# sanity check: a healthy Friture .app bundle is well under 200 MB.
# A much larger result usually means a packaging step duplicated the Qt/Python
# libs, so fail loudly rather than ship a bloated artifact.
APP_BUNDLE_SIZE_BYTES=$(du -sk dist/friture.app | awk '{print $1}')
echo "friture.app size: $APP_BUNDLE_SIZE_BYTES KB"
if [ "$APP_BUNDLE_SIZE_BYTES" -gt 200000 ]; then
    echo "ERROR: friture.app is unexpectedly large (>200MB); aborting."
    exit 1
fi

# Build the DMG with a polished layout (icon positioning + a drop zone for
# /Applications) using create-dmg.
brew install create-dmg

create-dmg \
    --volname "Friture" \
    --window-pos 200 122 \
    --window-size 600 400 \
    --icon-size 100 \
    --hide-extension "friture.app" \
    --icon "friture.app" 150 190 \
    --app-drop-link 450 190 \
    --background "installer/dmg-background.png" \
    --hdiutil-retries 30 \
    --no-internet-enable \
    "$ARTIFACT_FILENAME" \
    dist/friture.app

du -hs dist/friture.app
du -hs "$ARTIFACT_FILENAME"
