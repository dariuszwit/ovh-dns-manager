# ovh-manager.ps1 — robust launcher for PowerShell
# Steps:
# 1) Ensure Python launcher exists.
# 2) Recreate venv to avoid stale base interpreter path.
# 3) Activate venv in THIS PS session.
# 4) Upgrade pip and install requirements using venv's python.
# 5) Read port from ovh_accounts.json (fallback 8000).
# 6) Open browser and run app.py with detailed logging.

param([string]$PyArg = "-3.11")  # change to "-3.12" or "" if needed

cls
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
Set-Location $here
Write-Host "[INFO] Working dir: $here"

function Die($msg){ Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }

# --- Python launcher check ---
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
  Die "Python launcher 'py.exe' not found. Install Python for Windows (with 'py launcher')"
}
Write-Host "[INFO] Installed Pythons:"
try { & py -0p | ForEach-Object { Write-Host "       $_" } } catch { Write-Host "[WARN] Can't list Pythons: $($_.Exception.Message)" }

# --- Deactivate any prior venv in this PS session ---
if (Get-Command deactivate -ErrorAction SilentlyContinue) { deactivate | Out-Null }

# --- Recreate venv to avoid hardcoded path to removed base Python ---
if (Test-Path "$here\venv") {
  Write-Host "[INFO] Removing existing venv (avoid stale base interpreter)..."
  Remove-Item -Recurse -Force "$here\venv"
}
Write-Host "[INFO] Creating venv via: py $PyArg -m venv venv"
& py $PyArg -m venv venv

# --- Activate venv in CURRENT PS process ---
Set-ExecutionPolicy -Scope Process Bypass -Force | Out-Null
& "$here\venv\Scripts\Activate.ps1"

$venvPy = "$here\venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) { Die "venv python not found at $venvPy" }
& $venvPy --version | ForEach-Object { Write-Host "[INFO] Using $($_)" }

# --- Install deps using venv's python (never global pip wrapper) ---
Write-Host "[INFO] Upgrading pip..."
& $venvPy -m pip install --upgrade pip

Write-Host "[INFO] Installing dependencies from requirements.txt..."
& $venvPy -m pip install -r "$here\requirements.txt"

# --- Read port from JSON (fallback 8000) ---
$port = 8000
try {
  $cfg = Get-Content "$here\ovh_accounts.json" -Raw | ConvertFrom-Json
  if ($null -ne $cfg.port -and $cfg.port -is [int]) { $port = $cfg.port }
} catch {
  Write-Host "[WARN] Can't parse ovh_accounts.json: $($_.Exception.Message)"
}
Write-Host "[INFO] Port resolved: $port"

# --- Run app ---
Write-Host "[INFO] Opening http://127.0.0.1:$port/"
Start-Process "http://127.0.0.1:$port/"

Write-Host "[INFO] Starting Flask app (app.py) ..."
& $venvPy "$here\app.py"
$code = $LASTEXITCODE
Write-Host "[INFO] App exited with code $code"
exit $code
