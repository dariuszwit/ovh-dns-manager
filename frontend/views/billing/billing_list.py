from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import billing_bp


@billing_bp.route("/select_account", methods=["GET", "POST"])
@login_required
def select_account():
    from frontend.helpers.load_accounts import load_accounts
    accounts = load_accounts()

    if request.method == "POST":
        account = request.form.get("account")
        return redirect(url_for("frontend.billing.bill_list", account=account))

    return render_template("billing_select_account.html", accounts=accounts)


@billing_bp.route("/list", methods=["GET"])
@login_required
def bill_list():
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.billing.select_account"))

    bills = []

    try:
        bill_ids = client.get('/me/bill')
        bill_ids.sort(reverse=True)
        for bill_id in bill_ids[:50]:
            try:
                bill_info = client.get(f'/me/bill/{bill_id}')
                bills.append(bill_info)
            except Exception:
                bills.append({"billId": bill_id})
    except Exception as e:
        flash(f"Błąd pobierania faktur: {e}")

    # Sort by date desc
    bills.sort(key=lambda x: x.get('date', ''), reverse=True)

    return render_template("billing_list.html", account=account, bills=bills)
