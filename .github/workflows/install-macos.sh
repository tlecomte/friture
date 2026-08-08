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

# macos has random errors with hdiutil (used within create-dmg) because of XProtectBehaviorService, retry a few times.
# Reference: https://github.com/actions/runner-images/issues/7522#issuecomment-1556766641
max_retries=30
retry_delay_seconds=5

create_dmg_cmd=(
    create-dmg
    --volname "Friture"
    --window-pos 200 122
    --window-size 660 440
    --icon-size 110
    --hide-extension "friture.app"
    --icon "friture.app" 170 210
    --app-drop-link 440 210
    "$ARTIFACT_FILENAME"
    dist/friture.app
)

for ((i=1; i<=max_retries; i++)); do
    set +e  # Disable 'exit on error'
    "${create_dmg_cmd[@]}"
    status=$?
    set -e  # Re-enable 'exit on error'

    if [ $status -eq 0 ]; then
        echo "create-dmg succeeded on attempt $i"
        break
    else
        echo "create-dmg failed on attempt $i"
        # create-dmg leaves a partial .dmg on some failures; remove it so the
        # next attempt starts clean and the retry isn't masked by a stale file.
        rm -f "$ARTIFACT_FILENAME"
        if [ $i -lt $max_retries ]; then
            echo "Retrying in $retry_delay_seconds seconds..."
            sleep $retry_delay_seconds
        else
            echo "All attempts failed."
            exit 1
        fi
    fi
done

du -hs dist/friture.app
du -hs "$ARTIFACT_FILENAME"
