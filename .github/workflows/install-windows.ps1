Write-Host ""
Write-Host "==========================================="
Write-Host "Cleaning up"
Write-Host "==========================================="

Remove-Item "build" -Recurse -ErrorAction Ignore
Remove-Item "dist" -Recurse -ErrorAction Ignore

Write-Host ""
Write-Host "==========================================="
Write-Host "Packaging with pyinstaller"
Write-Host "==========================================="

uv run pyinstaller friture.spec -y --log-level=DEBUG

Write-Host ""
Write-Host "==========================================="
Write-Host "Archiving the package as a zip file"
Write-Host "==========================================="

Compress-Archive -Path .\dist\friture\* -DestinationPath .\dist\friture.zip

Write-Host ""
Write-Host "==========================================="
Write-Host "Read version from file"
Write-Host "==========================================="
$version = uv run python -c "import friture; print(friture.__version__)"
Write-Host $version

Write-Host ""
Write-Host "==========================================="
Write-Host "Build MSI with WiX"
Write-Host "==========================================="

& "$env:WIX/bin/heat.exe" dir "dist/friture" -cg FritureFiles -gg -scom -sreg -sfrag -srd -dr INSTALLFOLDER -out "dist/FritureFilesFragment.wxs"
& "$env:WIX/bin/candle.exe" installer/friture.wxs -dVersion="$version" -o dist/wixobj/ -arch x64
& "$env:WIX/bin/candle.exe" dist/FritureFilesFragment.wxs -o dist/wixobj/
& "$env:WIX/bin/light.exe" -ext WixUIExtension -cultures:en-us -b dist/friture dist/wixobj\*.wixobj -o "dist/friture-$version.msi"

# Installer can be tested with:
#    msiexec /i dist\friture-0.38.msi /l*v MyLogFile.txt
# for uninstall:
#    msiexec /x dist\friture-0.38.msi

Write-Host ""
Write-Host "==========================================="
Write-Host "Build MSIX package"
Write-Host "==========================================="

Copy-Item -Path .\dist\friture -Destination .\dist\friture-msix -Recurse
Copy-Item -Path resources\images\friture.iconset\icon_512x512.png -Destination .\dist\friture-msix\icon_512x512.png

# apply version to AppxManifest.xml and save it to the package folder.
$xml = [xml](Get-Content .\installer\appxmanifest.xml)
$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace("ns", $xml.DocumentElement.NamespaceURI)
$package = $xml.SelectSingleNode("//ns:Package", $ns)
$package.Identity.Version = "$version.0.0"
$xml.Save(".\dist\friture-msix\AppxManifest.xml")

# SignTool is omitted here on purpose,
# as Microsoft Store ingestion signs the final package.
MakeAppx pack /v /d .\dist\friture-msix /p ".\dist\friture-$version.msix"
