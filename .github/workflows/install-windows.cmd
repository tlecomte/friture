@echo off

powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0\install-windows.ps1' %* "
