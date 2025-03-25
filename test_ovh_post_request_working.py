import hashlib
import json
import requests

# Funkcja do pobrania timestamp z OVH API
def get_ovh_timestamp():
    url = "https://eu.api.ovh.com/1.0/auth/time"  # Endpoint do pobrania aktualnego czasu z serwera OVH
    response = requests.get(url)
    if response.status_code == 200:
        timestamp = response.text.strip()  # Pobranie timestamp
        print(f"✅ Retrieved timestamp from OVH: {timestamp}")
        return timestamp
    else:
        print("❌ Failed to retrieve timestamp from OVH")
        return None

# Funkcja do wysyłania zapytań do API OVH
def send_ovh_request(account, record):
    # Zmienne konfiguracyjne
    application_secret = account['application_secret']
    application_key = account['application_key']
    consumer_key = account['consumer_key']
    method = 'POST'
    url = 'https://eu.api.ovh.com/1.0/domain/zone/justdetox.it/record'
    
    # Pobierz aktualny timestamp z OVH
    timestamp = get_ovh_timestamp()
    if not timestamp:
        return

    print("✅ Starting request for account:", account['name'])
    print("📅 Timestamp:", timestamp)
    print("📍 Request method:", method)
    print("🌍 Request URL:", url)

    # Przygotowanie ciała zapytania
    body = json.dumps(record, separators=(',', ':'))  # Eliminujemy zbędne spacje w JSON
    print(f'✅ Body for {account["name"]}: {body}')  # Logowanie ciała zapytania

    # Logowanie przed generowaniem sygnatury
    to_sign = f'{application_secret}+{consumer_key}+{method}+{url}+{body}+{timestamp}'
    print(f'✅ ToSign (before hashing) for {account["name"]}:', to_sign)  # Logowanie ToSign
    
    # Generowanie sygnatury SHA-1
    signature = hashlib.sha1(to_sign.encode('utf-8')).hexdigest()  # Generowanie sygnatury SHA-1
    print(f'✅ Signature (without prefix) for {account["name"]}:', signature)  # Logowanie sygnatury przed dodaniem prefiksu

    # Dodanie prefiksu $1$ do sygnatury, jak w Postmanie
    signature_with_prefix = '$1$' + signature
    print(f'✅ Signature (with prefix $1$) for {account["name"]}:', signature_with_prefix)  # Logowanie sygnatury z prefiksem

    # Logowanie nagłówków
    headers = {
        'X-Ovh-Timestamp': timestamp,
        'X-Ovh-Consumer': consumer_key,
        'X-Ovh-Application': application_key,
        'X-Ovh-Signature': signature_with_prefix,  # Sygnatura z prefiksem '$1$'
        'Content-Type': 'application/json',
        'User-Agent': 'PostmanRuntime/7.43.2',  # Dodanie nagłówka User-Agent, jak w Postmanie
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }
    
    print("🔧 Request headers:")
    for key, value in headers.items():
        print(f"    {key}: {value}")  # Logowanie nagłówków zapytania

    # Tworzenie sesji HTTP
    session = requests.Session()

    # Wykonanie zapytania POST za pomocą sesji
    print("🔄 Sending request to OVH API...")
    response = session.post(url, headers=headers, data=body)

    # Logowanie statusu odpowiedzi
    print(f"📊 Status Code: {response.status_code}")
    print("💬 Response Headers:")
    for key, value in response.headers.items():
        print(f"    {key}: {value}")
    
    print("💥 Response Body:")
    try:
        print(json.dumps(response.json(), indent=4))  # Logowanie odpowiedzi w formacie JSON
    except ValueError:  # Jeśli odpowiedź nie jest w formacie JSON, logujemy surowe dane
        print(response.text)

    # Obsługa odpowiedzi
    if response.status_code == 200:
        print(f'✅ Success for {account["name"]}!')
        print("✅ Response:", response.json())
    else:
        print(f'❌ Error for {account["name"]}: {response.status_code}')
        print(response.text)

# Wczytywanie danych z pliku JSON
with open('ovh_accounts.json', 'r') as file:
    data = json.load(file)

# Przykładowe dane
record_list = [{
    "fieldType": "TXT",
    "subDomain": "",
    "target": "MS=ms333333333",  # Możesz zmienić na prawidłowy cel
    "ttl": 3600
}]

# Iterowanie przez konta i wysyłanie zapytań
for account in data['accounts']:
    print(f"🔑 Processing account: {account['name']}")
    record = record_list[0]  # W tym przykładzie tylko jeden rekord
    send_ovh_request(account, record)
