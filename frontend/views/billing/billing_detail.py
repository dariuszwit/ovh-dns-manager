from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import billing_bp


@billing_bp.route("/detail/<path:bill_id>", methods=["GET"])
@login_required
def bill_detail(bill_id):
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.billing.select_account"))

    bill = {}
    details = []

    try:
        bill = client.get(f'/me/bill/{bill_id}')
    except Exception as e:
        flash(f"Błąd pobierania faktury: {e}")

    try:
        detail_ids = client.get(f'/me/bill/{bill_id}/details')
        for did in detail_ids:
            try:
                d = client.get(f'/me/bill/{bill_id}/details/{did}')
                details.append(d)
            except Exception:
                details.append({"billDetailId": did})
    except Exception:
        pass

    return render_template(
        "billing_detail.html",
        account=account,
        bill=bill,
        bill_id=bill_id,
        details=details,
    )
