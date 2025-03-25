from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import domain_bp  # UŻYWAMY JUŻ ISTNIEJĄCEGO blueprinta

@domain_bp.route("/select_domain", methods=["GET"])
@login_required
def select_domain():
    account = request.args.get("account")
    print(f"\n🌐 [select_domain] Account received from GET param: {account}")

    client = get_client(account)
    if client is None:
        flash("Invalid account selected.")
        print("❌ [select_domain] No client returned. Redirecting...")
        return redirect(url_for("domain.select_account"))

    domains = []
    try:
        print(f"🔍 [select_domain] Attempting OVH GET /domain for account: {account}")
        domains = client.get('/domain')
        print(f"📦 /domain → {len(domains)} results")

        if not domains:
            print("⚠️ [select_domain] No domains from /domain – trying /domain/zone...")
            domains = client.get('/domain/zone')
            print(f"🌍 /domain/zone → {len(domains)} results")
    except Exception as e:
        flash(f"Error fetching domains: {e}")
        print(f"❌ [select_domain] Exception during OVH API call: {e}")
        domains = []

    return render_template("select_domain.html", account=account, domains=domains)
