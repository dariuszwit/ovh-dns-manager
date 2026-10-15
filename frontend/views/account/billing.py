from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import account_bp


@account_bp.route("/billing", methods=["GET"])
@login_required
def billing():
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.account.select_account"))

    bills = []

    try:
        bill_ids = client.get('/me/bill')
        for bill_id in bill_ids[:20]:
            try:
                bill_info = client.get(f'/me/bill/{bill_id}')
                bills.append(bill_info)
            except Exception:
                bills.append({"billId": bill_id})
    except Exception as e:
        flash(f"Błąd pobierania faktur: {e}")

    return render_template(
        "billing.html",
        account=account,
        bills=bills,
    )
