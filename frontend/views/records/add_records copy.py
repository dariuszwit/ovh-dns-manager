# frontend/views/records/add_records.py

from flask import request, redirect, url_for, flash
from ..auth.decorators import login_required
from frontend.helpers.get_record_types import get_record_types
from ..api.ovh_client import get_client
from . import records_bp
import json

# Funkcja do pobrania timestamp z OVH API
def get_ovh_timestamp():
    url = "https://eu.api.ovh.com/1.0/auth/time"
    response = requests.get(url)
    if response.status_code == 200:
        timestamp = response.text.strip()
        print(f"✅ Retrieved timestamp from OVH: {timestamp}")
        return timestamp
    else:
        print("❌ Failed to retrieve timestamp from OVH")
        return None

# Funkcja walidacji rekordu
def validate_record(record):
    allowed_record_types = ['TXT', 'A', 'CNAME']
    
    if not record.get('fieldType') or not record.get('target'):
        return False, "Record type and target are required"
    if record.get('fieldType') not in allowed_record_types:
        return False, f"Invalid record type: {record['fieldType']}"
    if record.get('fieldType') == "TXT" and len(record.get('target', "")) > 255:
        return False, "TXT record target is too long"
    return True, ""

# Funkcja do wysyłania zapytań do API OVH
def send_ovh_request(account, domain, record):
    application_secret = account['application_secret']
    application_key = account['application_key']
    consumer_key = account['consumer_key']
    method = 'POST'
    url = f'https://eu.api.ovh.com/1.0/domain/zone/{domain}/record'

    timestamp = get_ovh_timestamp()
    if not timestamp:
        return

    print("✅ Starting request for account:", account['name'])
    print("📅 Timestamp:", timestamp)
    print("📍 Request method:", method)
    print("🌍 Request URL:", url)

    response = client.post(url, record)
    print(f"✅ Response: {response}")
    return response


# Widok do dodawania rekordów
@records_bp.route("/add_records/<domain>", methods=["POST"])
@login_required
def add_records(domain):
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Invalid account selected.")
        print("❌ OVH client not initialized.")
        return redirect(url_for("frontend.select_account"))

    records_data = []
    try:
        count = int(request.form.get("number_of_records", 0))
        print(f"🔍 Number of records to add: {count}")
    except ValueError:
        flash("Invalid number of records.")
        return redirect(url_for("frontend.domain.manage_domain", domain=domain, account=account))

    # Przygotowanie rekordów do wysłania
    for i in range(count):
        rec_type = request.form.get(f"record_{i}_type")
        sub_domain = request.form.get(f"record_{i}_subDomain") or ""
        target = request.form.get(f"record_{i}_target") or ""
        ttl = request.form.get(f"record_{i}_ttl")

        if rec_type and target:
            target = target.strip()
            sub_domain = sub_domain.strip()

            if rec_type == "TXT":
                target = target.strip()

            if sub_domain == "@":
                sub_domain = ""

            record = {
                "fieldType": rec_type,
                "subDomain": sub_domain,
                "target": target,
                "ttl": int(ttl) if ttl and ttl.isdigit() else 3600
            }

            print(f"📦 RECORD TO SEND: {json.dumps(record)}")

            valid, error_message = validate_record(record)
            if not valid:
                flash(error_message)
                return redirect(url_for("frontend.domain.manage_domain", domain=domain, account=account))
            
            records_data.append(record)

    if not records_data:
        flash("No valid records provided.")
        return redirect(url_for("frontend.domain.manage_domain", domain=domain, account=account))

    errors = []
    for record in records_data:
        try:
            response = send_ovh_request(account, domain, record)
            print(f"✅ Record added successfully: {response}")
        except Exception as e:
            print(f"❌ ERROR adding record: {record} → {e}")
            errors.append(f"Error adding record {record}: {e}")

    # Odświeżenie strefy DNS tylko jeśli wszystkie rekordy zostały dodane pomyślnie
    if not errors:
        try:
            client.post(f'/domain/zone/{domain}/refresh')
            print("✅ DNS zone refreshed successfully.")
        except Exception as e:
            print(f"⚠️ WARNING: DNS zone refresh failed: {e}")
    else:
        print("⚠️ Skipping DNS zone refresh due to previous errors.")

    if errors:
        flash("Some errors occurred while adding records. Check logs for details.")
    else:
        flash("New records added successfully.")

    return redirect(url_for("frontend.domain.manage_domain", domain=domain, account=account))
