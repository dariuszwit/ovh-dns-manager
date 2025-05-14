@echo off
cd /d "%~dp0"
cls

echo 🔄 Instalacja wymaganych pakietów Python...
python -m pip install -r requirements.txt

echo ✅ Uruchamianie analizy danych...
python main.py --account 3

if %errorlevel% neq 0 (
    echo ❌ Nie udało się uruchomić skryptu!
) else (
    echo ✅ Skrypt zakończony pomyślnie.
)

pause
