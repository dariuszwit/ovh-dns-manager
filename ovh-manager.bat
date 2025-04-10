@echo off
REM Clear the console
cls

REM Check if the virtual environment folder "venv" exists; if not, create it
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo Error while creating virtual environment.
        pause
        exit /b 1
    )
) ELSE (
    echo Virtual environment already exists.
)

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Install required packages from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Error while installing dependencies.
    pause
    exit /b 1
)

REM Read the port from ovh_accounts.json using PowerShell
FOR /F "delims=" %%A IN ('powershell -Command "(Get-Content ovh_accounts.json | ConvertFrom-Json).port"') DO (
    SET PORT=%%A
)

REM Start the Flask application and open it in the browser
echo Starting Flask application on port %PORT%...
start "" http://127.0.0.1:%PORT%/
python app.py

pause
