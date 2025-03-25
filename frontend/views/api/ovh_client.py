import ovh
from frontend.helpers.load_accounts import load_accounts

def get_client(account_name):
    """Tworzy instancję klienta OVH dla podanego konta i loguje wszystkie szczegóły."""
    print(f"\n🛰️ [get_client] Requested account: '{account_name}'")

    accounts = load_accounts()
    print(f"📜 [get_client] Dostępne konta: {[a['name'] for a in accounts]}")

    account = next((a for a in accounts if a["name"] == account_name), None)

    if account is None:
        print(f"❌ [get_client] Konto '{account_name}' nie znalezione w pliku konfiguracyjnym.")
        return None

    try:
        client = ovh.Client(
            endpoint='ovh-eu',
            application_key=account["application_key"],
            application_secret=account["application_secret"],
            consumer_key=account["consumer_key"]
        )
        print(f"✅ [get_client] OVH API Client zainicjalizowany dla konta: {account_name}")
    except Exception as e:
        print(f"❌ [get_client] Błąd inicjalizacji klienta OVH: {e}")
        return None

    # 🧪 Sprawdź kto jest zalogowany i jakie ma uprawnienia
    try:
        me = client.get('/me')
        print(f"🧠 Zalogowano jako: {me.get('nichandle')} / {me.get('email')}")

        rights = client.get('/auth/currentCredential')
        print("🔐 Uprawnienia tokena:")
        for r in rights.get('rules', []):
            print(f"   → {r.get('method'):>6} {r.get('path')}")
    except Exception as e:
        print(f"⚠️ [get_client] Błąd pobierania informacji o tokenie: {e}")

    return client
