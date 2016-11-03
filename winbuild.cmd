@echo off

powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0\winbuild.ps1' %* "
