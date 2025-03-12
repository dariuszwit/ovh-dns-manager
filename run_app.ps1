# run_app.ps1
# This script sets up a Python virtual environment, installs required packages,
# and runs the Flask application (from app.py) in development mode.
# All comments are provided in English.

# Clear the console
Clear-Host

# Check if the virtual environment folder 'venv' exists; if not, create it.
if (-Not (Test-Path -Path "./venv")) {
    Write-Host "Creating virtual environment..."
    try {
        python -m venv venv
        Write-Host "Virtual environment created successfully."
    } catch {
        Write-Error "Error creating virtual environment: $_"
        exit 1
    }
} else {
    Write-Host "Virtual environment already exists."
}

# Activate the virtual environment
Write-Host "Activating virtual environment..."
try {
    .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated."
} catch {
    Write-Error "Error activating virtual environment: $_"
    exit 1
}

# Install required packages from requirements.txt
Write-Host "Installing dependencies from requirements.txt..."
try {
    pip install -r requirements.txt
    Write-Host "Dependencies installed successfully."
} catch {
    Write-Error "Error installing dependencies: $_"
    exit 1
}

# Run the Flask application from app.py in debug mode on localhost:8000.
Write-Host "Starting Flask application (development mode)..."
try {
    python app.py
} catch {
    Write-Error "Error starting Flask application: $_"
    exit 1
}



# Jeśli pojawią się komunikaty związane z polityką wykonywania skryptów, uruchom:
# powershell
# Copy
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Uruchom skrypt poleceniem:
# powershell
# Copy
# .\run_app.ps1