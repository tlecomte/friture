#!/bin/bash

set -x

which python3
python3 -c 'import sys; print(sys.version)'

pip3 install . 

# pyinstaller needs to have the extensions built explicitely
python3 setup.py build_ext --inplace

sudo apt-get update
sudo apt-get install -y desktop-file-utils # for desktop-file-validate, used by pkg2appimage

# when PyInstaller collect libraries, it ignores libraries that are not found on the host.
# Those missing libs prevent proper startup.
# For example, PyQt5 bundles Qt5 libs that depend on libxcb-xinerama.so.0
# which would not be bundled unless explicitly installed.
sudo apt-get install libxcb-xinerama0
sudo apt-get install libxkbcommon-x11-0

# dependencies to build PortAudio
sudo apt-get install -y libasound-dev
sudo apt-get install -y libjack-dev

# build PortAudio 19.7.0 from scratch (required for Jack fixes on distributions using PipeWire)
wget https://github.com/PortAudio/portaudio/archive/refs/tags/v19.7.0.tar.gz
tar -xvf v19.7.0.tar.gz
cd portaudio-19.7.0
./configure --prefix=$PWD/portaudio-install
make
make install
ls -laR portaudio-install
cd ..

pyinstaller friture.spec -y --log-level=DEBUG

cd appimage
wget -q https://github.com/AppImage/AppImages/raw/master/pkg2appimage -O ./pkg2appimage
chmod a+x ./pkg2appimage
bash -ex pkg2appimage friture.yml

cd ..
ls -la appimage/out

export ARTIFACT_FILENAME=friture-$(python3 -c 'import friture; print(friture.__version__)')-$(date +'%Y%m%d').AppImage
echo $ARTIFACT_FILENAME

mv appimage/out/Friture*.AppImage $ARTIFACT_FILENAME
du -hs $ARTIFACT_FILENAME
