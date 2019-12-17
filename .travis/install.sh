#!/bin/bash

set -x

source multibuild/common_utils.sh
source multibuild/travis_steps.sh
before_install

which python3
python3 -c 'import sys; print(sys.version)'

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
    # workaround for https://github.com/pypa/packaging-problems/issues/134
    # build-time dependencies define in `setup_requires` are resolved
    # on macOS Python with TLSv1, which is now disabled, so that fails
    pip3 install numpy==1.16.2
    pip3 install Cython==0.27.3
fi

pip3 install -r requirements.txt

# pysinstaller needs to have the extensions built explicitely
python3 setup.py build_ext --inplace

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
    # Macos    

    pip3 install -U pyinstaller==3.5

    pyinstaller friture.spec -y --onedir --windowed

    ls -la dist/*

    # prepare a dmg out of friture.app
    export ARTIFACT_FILENAME=friture-$(python3 -c 'import friture; print(friture.__version__)')-$(date +'%Y%m%d').dmg
    echo $ARTIFACT_FILENAME
    hdiutil create $ARTIFACT_FILENAME -volname "Friture" -fs HFS+ -srcfolder dist/friture.app
    du -hs dist/friture.app
    du -hs $ARTIFACT_FILENAME
else
    # Linux
    sudo apt-get update
    sudo apt-get install -y libportaudio2
    sudo apt-get install -y desktop-file-utils # for desktop-file-validate, used by pkg2appimage

    # about pep517, see https://github.com/pypa/pip/issues/6163
    pip3 install -U pyinstaller==3.5 --no-use-pep517

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
fi

