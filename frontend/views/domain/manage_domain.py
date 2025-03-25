from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from frontend.helpers.get_record_types import get_record_types
from ..api.ovh_client import get_client
from . import domain_bp

@domain_bp.route("/manage_domain/<domain>", methods=["GET", "POST"])
@login_required
def manage_domain(domain):
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Invalid account selected.")
        print("❌ ERROR: Invalid OVH account selected.")
        return redirect(url_for("frontend.domain.select_account"))

    try:
        record_ids = client.get(f'/domain/zone/{domain}/record')
        print(f"📌 Retrieved {len(record_ids)} record IDs.")
        records = [client.get(f'/domain/zone/{domain}/record/{rid}') for rid in record_ids]
        for rec in records:
            print(f"📌 Existing record: {rec}")
    except Exception as e:
        flash(f"Error fetching records: {e}")
        print(f"❌ ERROR fetching records: {e}")
        records = []

    record_types = get_record_types()  # Pobranie pełnej listy typów rekordów DNS

    return render_template("manage_domain.html", account=account, domain=domain, records=records, record_types=record_types)
