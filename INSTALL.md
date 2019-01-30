# Installing Friture for development

Most of Friture is written in Python. Some specific parts require prior compilation.

## Suggested steps for Windows

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

If all went well, Friture will open.

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

## Windows executable

To build an executable for Windows, with the python interpreter included, run:

```
pyinstaller friture.spec -y
```

You get a `dist` directory with `friture.exe` and a collection of dependencies (dlls and compiled python extensions), that can be bundled together in an installer.
