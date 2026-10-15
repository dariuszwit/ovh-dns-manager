@echo off
REM ovh-manager.cmd — universal starter that runs the PowerShell launcher
cls
setlocal EnableExtensions
cd /d "%~dp0"
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0ovh-manager.ps1" -PyArg "-3.11"
set ERR=%ERRORLEVEL%
echo [INFO] Exit code: %ERR%
exit /b %ERR%
