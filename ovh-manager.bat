@echo off
REM ============================================================================
REM ovh-manager.bat — robust universal starter for OVH API Manager (Windows)
REM No fragile FOR-backticks; uses GOTO flow to avoid CMD parser pitfalls.
REM Steps:
REM  1) Ensure Python launcher exists.
REM  2) (Re)create venv if missing or broken (fixes stale base like C:\Python313\python.exe).
REM  3) Activate venv.
REM  4) Upgrade pip and install requirements via "python -m pip".
REM  5) Read port from ovh_accounts.json via PowerShell -> temp file (no parentheses in CMD).
REM  6) Open browser and run app.py. Return proper exit code.
REM Customize Python version below (PY_ARG). Use -3.12 or "" for default.
REM ============================================================================

cls
setlocal EnableExtensions EnableDelayedExpansion

REM --- Configuration ---
set "PY_ARG=-3.11"

REM --- Move to script directory ---
cd /d "%~dp0"
echo [INFO] Working dir: %cd%

REM --- Check Python launcher ---
where py >nul 2>nul
if errorlevel 1 goto :NO_PY

echo [INFO] Detected Python:
py -V 2>&1

REM --- If venv missing -> create; else sanity-check ---
if exist "venv\Scripts\python.exe" goto :CHECK_VENV
goto :CREATE_VENV

:CHECK_VENV
"venv\Scripts\python.exe" --version >nul 2>&1
if errorlevel 1 goto :RECREATE_VENV
goto :ACTIVATE

:CREATE_VENV
echo [INFO] Creating virtual environment...
py %PY_ARG% -m venv venv
if errorlevel 1 goto :CREATE_VENV_FALLBACK
goto :ACTIVATE

:RECREATE_VENV
echo [WARN] Existing venv looks broken. Recreating...
rmdir /s /q venv
py %PY_ARG% -m venv venv
if errorlevel 1 goto :CREATE_VENV_FALLBACK
goto :ACTIVATE

:CREATE_VENV_FALLBACK
echo [WARN] Could not create venv with %PY_ARG%. Trying default Python...
py -m venv venv
if errorlevel 1 goto :FAIL_CREATE_VENV
goto :ACTIVATE

:ACTIVATE
call "venv\Scripts\activate.bat"
if errorlevel 1 goto :FAIL_ACTIVATE

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 goto :FAIL_PIP

if exist "requirements.txt" goto :INSTALL_REQ
echo [WARN] requirements.txt not found. Continuing without dependency install.
goto :READ_PORT

:INSTALL_REQ
echo [INFO] Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 goto :FAIL_REQ

:READ_PORT
set "PORT="
set "TMPP=%TEMP%\ovh_port_%RANDOM%%RANDOM%.txt"
REM Write port to a temp file via PowerShell (no parentheses for CMD to parse)
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "try { if (Test-Path 'ovh_accounts.json') { $p=(Get-Content -Raw 'ovh_accounts.json' | ConvertFrom-Json).port; if ($p) { [Console]::Out.Write($p) } } } catch { }" > "%TMPP%" 2>nul

if exist "%TMPP%" set /p PORT=<"%TMPP%"
if exist "%TMPP%" del "%TMPP%" 2>nul
if "%PORT%"=="" set "PORT=8000"
echo [INFO] Port resolved: %PORT%

echo [INFO] Opening http://127.0.0.1:%PORT%/
start "" "http://127.0.0.1:%PORT%/"

echo [INFO] Starting Flask app (app.py) ...
python app.py
set "ERR=%ERRORLEVEL%"

if "%ERR%"=="0" echo [INFO] app.py exited successfully.
if not "%ERR%"=="0" echo [ERROR] app.py exited with code %ERR%

pause
exit /b %ERR%

:NO_PY
echo [ERROR] Python launcher 'py.exe' not found. Install Python for Windows (with 'py' launcher), then retry.
pause
exit /b 1

:FAIL_CREATE_VENV
echo [ERROR] Failed to create virtual environment.
pause
exit /b 1

:FAIL_ACTIVATE
echo [ERROR] Failed to activate virtual environment.
pause
exit /b 1

:FAIL_PIP
echo [ERROR] pip upgrade failed.
pause
exit /b 1

:FAIL_REQ
echo [ERROR] Failed to install dependencies from requirements.txt.
pause
exit /b 1
