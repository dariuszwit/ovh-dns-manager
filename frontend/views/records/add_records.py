from . import records_bp
from flask import request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
import json
import hashlib
import requests
import os
import ipaddress

def get_account_config(account_name):
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ovh_accounts.json"))
    print(f"\n📂 [get_account_config] Absolutna ścieżka do ovh_accounts.json: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            accounts = data.get("accounts", [])
            print(f"✅ [get_account_config] Wczytano {len(accounts)} kont z pliku:")
            for acc in accounts:
                print(f"🔍  • {acc.get('name')} (typ: {type(acc)})")
            for acc in accounts:
                if acc.get("name") == account_name:
                    print(f"✅ [get_account_config] Znalazłem dopasowane konto: {acc['name']}")
                    print(f"     🔑 application_key: {acc.get('application_key')}")
                    print(f"     🔐 application_secret: {acc.get('application_secret')}")
                    print(f"     🧾 consumer_key: {acc.get('consumer_key')}")
                    return acc
            print(f"❌ [get_account_config] Nie znaleziono konta: {account_name}")
    except Exception as e:
        print(f"❌ [get_account_config] Błąd odczytu pliku ovh_accounts.json: {e}")

    return None

def get_ovh_timestamp():
    url = "https://eu.api.ovh.com/1.0/auth/time"
    response = requests.get(url)
    print(f"⏱️ OVH time API → {response.status_code}")
    if response.status_code == 200:
        timestamp = response.text.strip()
        print(f"✅ Timestamp: {timestamp} (type: {type(timestamp)})")
        return timestamp
    print("❌ Failed to fetch timestamp from OVH")
    return None

def send_ovh_request(account, domain, record):
    print(f"\n🔧 send_ovh_request() CALLED")
    print(f"📟 account: {account} (type: {type(account)})")
    print(f"🌐 domain: {domain} (type: {type(domain)})")
    print(f"📆 record: {record} (type: {type(record)})")

    if not isinstance(record, dict):
        print(f"❌ ERROR: record must be a dict, got {type(record)}: {record}")
        return

    application_secret = account['application_secret']
    application_key = account['application_key']
    consumer_key = account['consumer_key']
    method = 'POST'
    url = f'https://eu.api.ovh.com/1.0/domain/zone/{domain}/record'

    timestamp = get_ovh_timestamp()
    if not timestamp:
        return

    try:
        body = json.dumps(record, separators=(',', ':'))
        print(f"📆 Body JSON: {body} (type: {type(body)})")
    except Exception as e:
        print(f"❌ Error serializing body: {e}")
        return

    to_sign = f"{application_secret}+{consumer_key}+{method}+{url}+{body}+{timestamp}"
    signature = '$1$' + hashlib.sha1(to_sign.encode('utf-8')).hexdigest()
    print(f"🔑 Signature: {signature}")

    headers = {
        'X-Ovh-Timestamp': timestamp,
        'X-Ovh-Consumer': consumer_key,
        'X-Ovh-Application': application_key,
        'X-Ovh-Signature': signature,
        'Content-Type': 'application/json',
        'User-Agent': 'PostmanRuntime/7.43.2',
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }

    print("📄 Headers:")
    for k, v in headers.items():
        print(f"   - {k}: {v} (type: {type(v)})")

    session = requests.Session()
    print("🚀 Sending request to OVH...")
    response = session.post(url, headers=headers, data=body)

    print(f"📊 Status: {response.status_code}")
    try:
        print("💬 Response:")
        print(json.dumps(response.json(), indent=4))
    except Exception:
        print(response.text)

# 🌐 Widok dodawania rekordów DNS
@records_bp.route("/add_records/<domain>", methods=["POST"], endpoint="add_records")
@login_required
def add_records(domain):
    print(f"\n🔄 add_records() called for domain: {domain}")
    account_name = request.args.get("account")
    print(f"📟 Raw account name: {account_name} (type: {type(account_name)})")

    account = get_account_config(account_name)
    if account is None:
        flash("Invalid OVH account selected.")
        return redirect(url_for("frontend.select_account"))

    client = get_client(account_name)
    if client is None:
        flash("OVH client initialization failed.")
        return redirect(url_for("frontend.select_account"))

    try:
        count = int(request.form.get("number_of_records", 0))
        print(f"🕧 number_of_records: {count}")
    except ValueError:
        flash("Invalid number of records.")
        return redirect(url_for("frontend.domain.manage_domain", domain=domain, account=account_name))

    records_data = []
    for i in range(count):
        rec_type = request.form.get(f"record_{i}_type")
        sub_domain = request.form.get(f"record_{i}_subDomain") or ""
        target = request.form.get(f"record_{i}_target") or ""
        ttl = request.form.get(f"record_{i}_ttl")

        print(f"\n➞️ Processing record {i}:")
        print(f"   rec_type: {rec_type}")
        print(f"   sub_domain: {sub_domain}")
        print(f"   target: {target}")
        print(f"   ttl: {ttl}")

        if not rec_type or not target:
            continue

        rec_type = rec_type.strip().upper()
        sub_domain = sub_domain.strip() if sub_domain != "@" else ""
        target = target.strip()
        ttl_value = int(ttl) if ttl and ttl.isdigit() else 3600

        if rec_type in ("A", "AAAA"):
            try:
                ip = ipaddress.ip_address(target)
                if rec_type == "A" and ip.version != 4:
                    raise ValueError("IPv6 provided for A record")
                if rec_type == "AAAA" and ip.version != 6:
                    raise ValueError("IPv4 provided for AAAA record")
            except ValueError as ve:
                flash(f"Rekord {rec_type} #{i+1} zawiera niepoprawny adres IP: {target}")
                print(f"❌ Invalid IP for {rec_type} record: {ve}")
                continue

        if rec_type == "MX":
            priority = request.form.get(f"record_{i}_priority")
            print(f"📥 MX Priority input: {priority}")
            if priority and priority.isdigit():
                target = f"{priority} {target}"
                print(f"📌 MX target z priorytetem: {target}")
            else:
                flash(f"Rekord MX #{i+1} wymaga poprawnego priorytetu.")
                print(f"❌ Missing/invalid MX priority for record {i}")
                continue

        elif rec_type == "SRV":
            priority = request.form.get(f"record_{i}_priority")
            weight = request.form.get(f"record_{i}_weight")
            port = request.form.get(f"record_{i}_port")
            print(f"🔹 SRV Fields → priority: {priority}, weight: {weight}, port: {port}")

            if not all([priority, weight, port]) or not (priority.isdigit() and weight.isdigit() and port.isdigit()):
                flash(f"Rekord SRV #{i+1} wymaga poprawnych wartości priority, weight, port.")
                print(f"❌ Invalid SRV parameters for record {i}")
                continue

            target = f"{priority} {weight} {port} {target}"
            print(f"🔎 SRV Full target: {target}")

        elif rec_type == "CNAME":
            if not target.endswith('.'):
                flash(f"Rekord CNAME #{i+1} powinien kończyć się kropką (np. example.com.)")
                print(f"⚠️ CNAME target bez kropki: {target}")
                target += '.'

        record = {
            "fieldType": rec_type,
            "subDomain": sub_domain,
            "target": target,
            "ttl": ttl_value
        }

        print(f"📆 RECORD TO SEND: {json.dumps(record)}")
        records_data.append(record)

    if not records_data:
        flash("No valid records to add.")
        return redirect(url_for("frontend.domain.manage_domain", domain=domain, account=account_name))

    errors = []
    for record in records_data:
        try:
            send_ovh_request(account, domain, record)
        except Exception as e:
            print(f"❌ Exception adding record: {record} → {e}")
            errors.append(str(e))

    if not errors:
        try:
            client.post(f'/domain/zone/{domain}/refresh')
            print("✅ DNS zone refreshed")
        except Exception as e:
            print(f"⚠️ DNS zone refresh failed: {e}")
    else:
        print("⚠️ Skipping DNS zone refresh due to errors")

    flash("New records added." if not errors else "Some errors occurred.")
    return redirect(url_for("frontend.domain.manage_domain", domain=domain, account=account_name))
