import json
import os

def load_accounts():
    path = os.path.abspath("ovh_accounts.json")
    print(f"\n📂 [load_accounts] Absolutna ścieżka do pliku: {path}")
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            accounts = data.get("accounts", [])
            print(f"✅ [load_accounts] Wczytano {len(accounts)} kont:")
            for a in accounts:
                print(f"🔐  → {a['name']}:")
                print(f"     🔑 application_key: {a.get('application_key')}")
                print(f"     🔐 application_secret: {a.get('application_secret')}")
                print(f"     🧾 consumer_key: {a.get('consumer_key')}")
            return accounts
    except Exception as e:
        print(f"❌ [load_accounts] Błąd wczytywania kont: {e}")
        return []
