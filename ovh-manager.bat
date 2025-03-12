@echo off
REM Clear the console
cls

REM Check if the virtual environment folder "venv" exists; if not, create it.
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo Error creating virtual environment.
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
    echo Error installing dependencies.
    pause
    exit /b 1
    )

REM Start the Flask application and open the dashboard
echo Starting Flask application (development mode)...
start "" http://127.0.0.1:8000/
python app.py

pause
