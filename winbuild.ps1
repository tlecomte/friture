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
Write-Host "Installing requirements"
Write-Host "==========================================="

& pip install -r requirements.txt

Write-Host ""
Write-Host "==========================================="
Write-Host "Installing pyinstaller"
Write-Host "==========================================="

# install a version of pefile that does not use the past library, which in turn imports too many things
& pip install git+https://github.com/tlecomte/pefile.git@tlecomte-remove-past

# install a recent pyinstaller with no need for mscvr*.dll, and that lets python35.dll be signed
& pip install -U git+https://github.com/pyinstaller/pyinstaller.git@469f1fa19275e415110f783fd538ad46805edff4

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
Write-Host "Archiving the package as a zip file"
Write-Host "==========================================="
Compress-Archive -Path .\dist\friture\* -DestinationPath .\dist\friture.zip

Write-Host ""
Write-Host "==========================================="
Write-Host "Building the NSIS installer"
Write-Host "==========================================="

& makensis.exe installer\friture-setup.nsi
