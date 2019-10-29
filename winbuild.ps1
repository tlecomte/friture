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

Write-Host "WIX env var set to " $env:WIX

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
Write-Host "Replace icudt53.dll with smaller version"
Write-Host "==========================================="

Copy-Item -Path "installer\icudt53.dll" -Destination "dist\friture\icudt53.dll"

Write-Host ""
Write-Host "==========================================="
Write-Host "Archiving the package as a zip file"
Write-Host "==========================================="

Compress-Archive -Path .\dist\friture\* -DestinationPath .\dist\friture.zip

Write-Host ""
Write-Host "==========================================="
Write-Host "Read version from file"
Write-Host "==========================================="
$initFileContent = Get-Content "friture/__init__.py"
$version = $initFileContent | Select-String '__version__ = \"([\d\.]+)\"' | Foreach-Object {$_.Matches.Groups[1].Value} 

Write-Host $version

Write-Host ""
Write-Host "==========================================="
Write-Host "Build MSI with WiX"
Write-Host "==========================================="

& "$env:WIX/bin/heat.exe" dir "dist/friture" -cg FritureFiles -gg -scom -sreg -sfrag -srd -dr INSTALLFOLDER -out "dist/FritureFilesFragment.wxs"
& "$env:WIX/bin/candle.exe" installer/friture.wxs -dVersion="$version" -o dist/wixobj/
& "$env:WIX/bin/candle.exe" dist/FritureFilesFragment.wxs -o dist/wixobj/
& "$env:WIX/bin/light.exe" -ext WixUIExtension -cultures:en-us -b dist/friture dist/wixobj\*.wixobj -o "dist/friture-$version.msi"

# Installer can be tested with:
#    msiexec /i dist\friture-0.38.msi /l*v MyLogFile.txt
# for uninstall:
#    msiexec /x dist\friture-0.38.msi
