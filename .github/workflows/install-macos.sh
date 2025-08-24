#!/bin/bash

set -x

which python3
python3 -c 'import sys; print(sys.version)'

pip3 install .

# pyinstaller needs to have the extensions built explicitely
python3 setup.py build_ext --inplace

# for Macos Big Sur, the stable portaudio (19.6.0) makes Friture freeze on startup
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

pyinstaller friture.spec -y

ls -la dist/*

# compare the portaudio libs to make sure the package contains the one that was installed with brew
ls -la /usr/local/lib/libportaudio.dylib
ls -la /usr/local/Cellar/portaudio/*/lib/libportaudio*.dylib
ls -la dist/friture.app/Contents/Frameworks/_sounddevice_data/portaudio-binaries

# PyInstaller will try to codesign friture.app, but will fail because of the Qt5 file structure
# (this is visible in the logs)
# see https://github.com/pyinstaller/pyinstaller/wiki/Recipe-OSX-Code-Signing-Qt
# so we fix the folder names and then sign again manually
python3 installer/fix_app_qt_folder_names_for_codesign.py dist/friture.app
codesign -s - --force --all-architectures --timestamp --deep dist/friture.app
codesign -dv dist/friture.app

# prepare a dmg out of friture.app
export ARTIFACT_FILENAME=friture-$(python3 -c 'import friture; print(friture.__version__)')-$(date +'%Y%m%d').dmg
echo $ARTIFACT_FILENAME

# macos has random hdiutil errors because of XProtectBehaviorService, retry a few times.
# Reference: https://github.com/actions/runner-images/issues/7522#issuecomment-1556766641
max_retries=30
retry_delay_seconds=5

for ((i=1; i<=max_retries; i++)); do
    set +e  # Disable 'exit on error'
    hdiutil create $ARTIFACT_FILENAME -volname "Friture" -fs HFS+ -srcfolder dist/friture.app
    status=$?
    set -e  # Re-enable 'exit on error'

    if [ $status -eq 0 ]; then
        echo "hdiutil create succeeded on attempt $i"
        break
    else
        echo "hdiutil create failed on attempt $i"
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
du -hs $ARTIFACT_FILENAME
