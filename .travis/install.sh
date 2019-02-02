#!/bin/bash

set -x

source multibuild/common_utils.sh
source multibuild/travis_steps.sh
before_install

which python3
python3 -c 'import sys; print(sys.version)'

pip3 install -r requirements.txt

# py2app chokes when the extensions are not built explicitely
python3 setup.py build_ext --inplace

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
    # Macos
    pip3 install -U "py2app==0.14"
    python3 setup.py py2app
    # prepare a dmg out of friture.app
    export ARTIFACT_FILENAME=friture-$(python3 -c 'import friture; print(friture.__version__)')-$(date +'%Y%m%d').dmg
    echo $ARTIFACT_FILENAME
    hdiutil create $ARTIFACT_FILENAME -volname "Friture" -fs HFS+ -srcfolder ../friture-dist/
    du -hs ../friture-dist/friture.app
    du -hs $ARTIFACT_FILENAME
else
    # Linux
    sudo apt-get update
    sudo apt-get install -y libportaudio0

    pip install -U pyinstaller

    pyinstaller friture.spec -y --log-level=DEBUG

    ls -la dist

    wget -q https://github.com/AppImage/AppImages/raw/master/pkg2appimage -O ./pkg2appimage
    chmod a+x ./pkg2appimage
    bash -ex pkg2appimage recipes/friture.yml

    ls -la out
fi

