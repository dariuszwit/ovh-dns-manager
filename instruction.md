# 1. Połącz się przez SSH do Cyber_Folks
ssh twoj_login@linis.it

# 2. Przejdź do katalogu aplikacji
clear && cd /home/akutdbtjhx/ovh-manager

# 3. Aktywuj środowisko wirtualne Python dla aplikacji
source /home/akutdbtjhx/virtualenv/ovh-manager/3.11/bin/activate

# 4. Zainstaluj pakiety wymagane przez aplikację
pip install -r requirements.txt

# 5. Ustaw bezpieczne uprawnienia dla plików konfiguracyjnych JSON
chmod 600 ovh_accounts.json users.json

# 6. Sprawdź poprawność ścieżki w passenger_wsgi.py (zaktualizuj, jeśli potrzeba):
# INTERP = "/home/akutdbtjhx/virtualenv/ovh-manager/3.11/bin/python3"

# 7. Upewnij się, że struktura plików wygląda następująco:
# ------------------------------------------
# /home/akutdbtjhx/ovh-manager/
# ├── public/
# ├── tmp/
# ├── passenger_wsgi.py
# ├── ovh-manager.py
# ├── requirements.txt
# ├── ovh_accounts.json
# ├── users.json
# ├── templates/
# │   ├── login.html
# │   └── dashboard.html
# └── static/
#     └── style.css
# ------------------------------------------

# 8. Konfiguracja aplikacji Python w DirectAdmin (Cyber_Folks):
# Application startup file: Passenger_wsgi.py
# Application Entry point: application

# 9. Treść pliku .htaccess:
# ------------------------------------------
# PassengerEnabled On
# PassengerAppRoot /home/akutdbtjhx/ovh-manager
# PassengerAppType wsgi
# PassengerStartupFile passenger_wsgi.py
#
# RewriteEngine On
# RewriteCond %{REQUEST_FILENAME} !-f
# RewriteRule ^(.*)$ /passenger_wsgi.py/$1 [QSA,L]
# ------------------------------------------

# 10. Restart aplikacji:
touch tmp/restart.txt

# 11. Logi błędów aplikacji:
tail -f ~/ovh-manager/stderr.log

# ------------------------------------------
# Wersja komend (jedna pod drugą do skopiowania i wklejenia):
ssh twoj_login@linis.it
cd /home/akutdbtjhx/ovh-manager
source /home/akutdbtjhx/virtualenv/ovh-manager/3.11/bin/activate
pip install -r requirements.txt
chmod 600 ovh_accounts.json users.json
touch tmp/restart.txt
tail -f ~/ovh-manager/stderr.log
