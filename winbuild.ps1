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

& pip install -U pyinstaller==4.4

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

# icudt53.dll is huge but needed for Qt
# A stripped down version is available here:
# https://forum.qt.io/topic/37891/minimal-icudt51-dll-icudt52-dll-and-icudt53-dll
# http://qlcplus.sourceforge.net/icudt53.dll
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

Write-Host ""
Write-Host "==========================================="
Write-Host "Build appx package"
Write-Host "==========================================="

Copy-Item -Path .\dist\friture -Destination .\dist\friture-appx -Recurse
Copy-Item -Path resources\images\friture.iconset\icon_512x512.png -Destination .\dist\friture-appx\icon_512x512.png

# apply version to appxmanifest.xml and save it to the dist folder
$xml = [xml](Get-Content .\installer\appxmanifest.xml)
$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace("ns", $xml.DocumentElement.NamespaceURI)
$package = $xml.SelectSingleNode("//ns:Package", $ns)
$package.Identity.Version = "$version.0.0"
$xml.Save(".\dist\friture-appx\appxmanifest.xml")

MakeAppx pack /v /d .\dist\friture-appx /p ".\dist\friture-$version.appx"
