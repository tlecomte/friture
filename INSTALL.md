# Installing Friture

## Binary releases

Get the latest binary releases for Windows, macOS and Linux on the [Releases](https://github.com/tlecomte/friture/releases) page.

## Running Friture from source on Linux

The following steps can be used to prepare a development environment for Friture on Ubuntu.

Prerequisite: a 64 bits Linux installation (PyQt5 wheels for Linux are only available for 64 bits).

This has been tested in a Virtualbox image for Ubuntu Trusty 16.04 LTS 64 bits from osboxes.org. The following custom settings have been set on the VM: increase video memory, enable 3d acceleration, enable audio input, install guest addition, add user to vboxsf (for file sharing with the host), keyboard layout setup.

1. Install git
```
sudo apt-get update
sudo apt-get install -y git
```

2. Install `portaudio` (used for audio IO in Friture)
```
sudo apt-get install -y libportaudio2
```

3. Install python 3.9 and related build tools
```
sudo apt-get install -y python3.9-dev
```

4. Clone the repository
```
git clone https://github.com/tlecomte/friture.git
cd friture
```

5. Optional: switch to a specific branch
```
git fetch
git checkout origin/<branchName>
```

6. Update `pip`, `setuptools` and `virtualenv`

```
sudo python3.9 -m pip install --upgrade pip
sudo pip3.9 install --upgrade setuptools
sudo pip3.9 install --upgrade virtualenv
```

7. Create a virtualenv and activate it
```
virtualenv  -p /usr/bin/python3.9 buildenv
source ./buildenv/bin/activate
```

8. Install Friture requirements (PyQt5, etc.)
```
pip3.9 install -r requirements.txt
```

9. Build Cython extensions
```
python3.9 setup.py build_ext --inplace
```

10. Run Friture
```
python3.9 main.py
```

## Running Friture from source on Windows

The following steps can be used to prepare a development environment for Friture on Windows.

1. Clone this repo

2. Install *chocolatey* from https://chocolatey.org/install

2. Install Python and Microsoft Visual Studio C++ Build Tools, required to build Friture. With chocolatey, in an administrator terminal:

```
choco install -y choco\packages.config
```

Watch out for a message indicating that a reboot is necessary.

The next commands do not need to be run in an administrator terminal.

4. Make sure pip is up-to-date:

```
python -m pip install --upgrade pip
```

5. Install virtualenv:

```
pip install -U virtualenv
```

6. Build a virtualenv:

```
virtualenv buildenv
```

7. Activate the virtualenv

```
.\buildenv\Scripts\activate
```

8. Install dependencies

```
pip install -r requirements.txt
```

9. Build Cython extensions

```
python setup.py build_ext --inplace
```

10. Run Friture

```
python main.py
```

## Dependencies

See [requirements.txt](requirements.txt)

## UI and resource files

If `friture.ui` or `resource.qrc` are changed, the corresponding python files need to be rebuilt:

```
pyuic4 ui/friture.ui --from-imports > friture/ui_friture.py
pyuic4 ui/settings.ui --from-imports > friture/ui_settings.py
pyrcc4 resources/friture.qrc -o friture/friture_rc.py
```

## Filters parameters

The filters parameters are precomputed in a file called `generated_filters.py`. To rebuild this file,
run the script named `filter_design.py`.
