$virtualenv = "buildenv"

# check for python and pip in PATH

$pythonPath = Get-Command "python" -ErrorAction SilentlyContinue
if ($pythonPath -eq $null)
{
   throw "Unable to find python in PATH"
}

Write-Host "python found in " $pythonPath.Definition

$pipPath = Get-Command "pip" -ErrorAction SilentlyContinue
if ($pipPath -eq $null)
{
    # try to add the Python Scripts folder to the path
    $pythonPath = Get-Command "python" | Select-Object -ExpandProperty Definition | Split-Path
    $env:Path += ";$pythonPath\Scripts"

    # retry
    $pipPath = Get-Command "pip" -ErrorAction SilentlyContinue
    if ($pipPath -eq $null)
    {
        throw "Unable to find pip in PATH"
    }
}

Write-Host "pip found in " $pipPath.Definition

$nsisPath = Get-Command "makensis" -ErrorAction SilentlyContinue
if ($nsisPath -eq $null)
{
    # try with the standard NSIS location
    $env:Path += ";C:\Program Files (x86)\NSIS"

    $nsisPath = Get-Command "makensis" -ErrorAction SilentlyContinue
    if ((Get-Command "makensis" -ErrorAction SilentlyContinue) -eq $null)
    {
        throw "Unable to find makensis in PATH. Install NSIS using the official installer or using chocolatey."
    }
}

Write-Host "makensis found in " $nsisPath.Definition

Write-Host ""
Write-Host "==========================================="
Write-Host "Cleaning up"
Write-Host "==========================================="

Remove-Item $virtualenv -Recurse -ErrorAction Ignore
Remove-Item "build" -Recurse -ErrorAction Ignore
Remove-Item "dist" -Recurse -ErrorAction Ignore

Write-Host ""
Write-Host "==========================================="
Write-Host "Making sure pip is up-to-date"
Write-Host "==========================================="

& python -m pip install --upgrade pip

Write-Host ""
Write-Host "==========================================="
Write-Host "Making sure setuptools is up-to-date (for compiler compatibility)"
Write-Host "==========================================="

& pip install --upgrade setuptools

Write-Host ""
Write-Host "==========================================="
Write-Host "Installing virtualenv"
Write-Host "==========================================="

& pip install -U virtualenv

Write-Host ""
Write-Host "==========================================="
Write-Host "Creating a virtualenv"
Write-Host "==========================================="

& virtualenv $virtualenv

Write-Host ""
Write-Host "==========================================="
Write-Host "Activating the virtualenv"
Write-Host "==========================================="

& "$virtualenv\Scripts\activate"

Write-Host ""
Write-Host "==========================================="
Write-Host "Installing Numpy, Scipy custom wheels"
Write-Host "==========================================="

# copied from http://www.lfd.uci.edu/~gohlke/pythonlibs/
& pip install https://www.dropbox.com/s/4dkx7yvdqfahsxi/numpy-1.11.2%2Bmkl-cp35-cp35m-win32.whl?dl=1
& pip install https://www.dropbox.com/s/bilym1blfykd0za/scipy-0.18.1-cp35-cp35m-win32.whl?dl=1

Write-Host ""
Write-Host "==========================================="
Write-Host "Applying Scipy tweaks"
Write-Host "==========================================="

# Fix Scipy massive imports by replacing 2 init files by empty files
Rename-Item "$virtualenv\lib\site-packages\scipy\interpolate\__init__.py" __init__.py.bak *>$null
Rename-Item "$virtualenv\lib\site-packages\scipy\signal\__init__.py" __init__.py.bak *>$null
New-Item -ItemType file "$virtualenv\lib\site-packages\scipy\interpolate\__init__.py" *>$null
New-Item -ItemType file "$virtualenv\lib\site-packages\scipy\signal\__init__.py" *>$null

Write-Host ""
Write-Host "==========================================="
Write-Host "Installing all other requirements"
Write-Host "==========================================="

& pip install -r requirements.txt

Write-Host ""
Write-Host "==========================================="
Write-Host "Installing pyinstaller"
Write-Host "==========================================="

& pip install git+https://github.com/tlecomte/pefile.git@tlecomte-remove-past
& pip install -U pyinstaller

Write-Host ""
Write-Host "==========================================="
Write-Host "Building Cython extensions"
Write-Host "==========================================="

& python setup.py build_ext --inplace

Write-Host ""
Write-Host "==========================================="
Write-Host "Packaging with pyinstaller"
Write-Host "==========================================="

& pyinstaller friture.spec -y --log-level=DEBUG

Write-Host ""
Write-Host "==========================================="
Write-Host "Building the NSIS installer"
Write-Host "==========================================="

& makensis.exe installer\friture-setup.nsi
