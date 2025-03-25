import ovh
import json
import os
import sys

print("\n🔍 Loading OVH credentials from file: ovh_accounts.json")

# Pełna ścieżka do ovh_accounts.json
json_path = os.path.abspath("ovh_accounts.json")
print(f"📂 Absolutna ścieżka do pliku: {json_path}")

# Wczytaj dane kont
try:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        accounts = data.get("accounts", [])
        print(f"✅ Wczytano {len(accounts)} kont z pliku.")
except Exception as e:
    print(f"❌ Błąd wczytywania pliku JSON: {e}")
    sys.exit(1)

# Nazwa konta, które chcemy sprawdzić
account_name = "ZGI"

# Znajdź dane dla konta ZGI
account = next((a for a in accounts if a["name"] == account_name), None)

if not account:
    print(f"❌ Konto '{account_name}' nie zostało znalezione w pliku.")
    sys.exit(1)

print(f"\n🔐 Dane konta '{account_name}':")
print(f"   🔑 application_key: {account['application_key']}")
print(f"   🔐 application_secret: {account['application_secret']}")
print(f"   🧾 consumer_key: {account['consumer_key']}")

# Inicjalizacja klienta OVH
print("\n🚀 Tworzę klienta OVH...")
try:
    client = ovh.Client(
        endpoint='ovh-eu',
        application_key=account["application_key"],
        application_secret=account["application_secret"],
        consumer_key=account["consumer_key"]
    )
    print("✅ Klient OVH zainicjalizowany.")
except Exception as e:
    print(f"❌ Błąd tworzenia klienta OVH: {e}")
    sys.exit(1)

# Pobierz informacje o właścicielu konta
print("\n🔎 Zapytanie: GET /me")
try:
    me = client.get('/me')
    print(f"🧠 Połączono jako: {me.get('nichandle')} / {me.get('email')}")
except Exception as e:
    print(f"❌ Błąd zapytania /me: {e}")
    sys.exit(1)

# Pobierz uprawnienia tokena
print("\n🔎 Zapytanie: GET /auth/currentCredential")
try:
    rights = client.get('/auth/currentCredential')
    print("🔐 Uprawnienia tokena:")
    for r in rights.get("rules", []):
        print(f"   → {r['method']:>6} {r['path']}")
except Exception as e:
    print(f"❌ Błąd zapytania /auth/currentCredential: {e}")

# Spróbuj pobrać domeny
print("\n🔎 Zapytanie: GET /domain")
try:
    domains = client.get('/domain')
    print(f"📦 Liczba domen widocznych przez API: {len(domains)}")
    if domains:
        for d in domains:
            print(f"   • {d}")
    else:
        print("⚠️  Brak widocznych domen – próbuję /domain/zone jako alternatywę...")
        raise ValueError("Brak domen – spróbujmy /domain/zone")
except Exception as e:
    print(f"ℹ️ Info: {e}")
    print("\n🔎 Zapytanie: GET /domain/zone")
    try:
        zones = client.get('/domain/zone')
        print(f"🌍 Liczba stref DNS widocznych przez API: {len(zones)}")
        if zones:
            for z in zones:
                print(f"   • {z}")
        else:
            print("⚠️  Brak widocznych stref DNS – upewnij się, że token ma dostęp.")
    except Exception as z:
        print(f"❌ Błąd zapytania /domain/zone: {z}")
