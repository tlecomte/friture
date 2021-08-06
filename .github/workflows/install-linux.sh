#!/bin/bash

set -x

which python3
python3 -c 'import sys; print(sys.version)'

pip3 install -r requirements.txt

# pyinstaller needs to have the extensions built explicitely
python3 setup.py build_ext --inplace

sudo apt-get update
sudo apt-get install -y libportaudio2
sudo apt-get install -y desktop-file-utils # for desktop-file-validate, used by pkg2appimage

pip3 install -U pyinstaller==4.4

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
