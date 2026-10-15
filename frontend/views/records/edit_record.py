from flask import request, jsonify
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import records_bp


@records_bp.route("/edit_record/<domain>/<int:record_id>", methods=["POST"])
@login_required
def edit_record(domain, record_id):
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        return jsonify({"success": False, "error": "Invalid account selected."}), 400

    sub_domain = request.form.get("subDomain", "")
    target = request.form.get("target", "")
    ttl = request.form.get("ttl", "3600")

    try:
        ttl_value = int(ttl)
    except ValueError:
        ttl_value = 3600

    payload = {
        "subDomain": sub_domain,
        "target": target,
        "ttl": ttl_value
    }

    try:
        client.put(f'/domain/zone/{domain}/record/{record_id}', **payload)
        print(f"✅ Record {record_id} updated: {payload}")
    except Exception as e:
        print(f"❌ Error updating record {record_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

    try:
        client.post(f'/domain/zone/{domain}/refresh')
        print("✅ DNS zone refreshed after edit")
    except Exception as e:
        print(f"⚠️ DNS zone refresh failed after edit: {e}")

    return jsonify({"success": True})
