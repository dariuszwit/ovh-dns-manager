from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import account_bp


@account_bp.route("/select_account", methods=["GET", "POST"])
@login_required
def select_account():
    from frontend.helpers.load_accounts import load_accounts
    accounts = load_accounts()

    if request.method == "POST":
        account = request.form.get("account")
        return redirect(url_for("frontend.account.account_info", account=account))

    return render_template("account_select_account.html", accounts=accounts)


@account_bp.route("/info", methods=["GET"])
@login_required
def account_info():
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.account.select_account"))

    me_info = {}
    services = []

    try:
        me_info = client.get('/me')
    except Exception as e:
        flash(f"Błąd pobierania danych konta: {e}")

    try:
        service_ids = client.get('/services')
        for sid in service_ids[:30]:
            try:
                svc_info = client.get(f'/services/{sid}')
                services.append(svc_info)
            except Exception:
                services.append({"serviceId": sid})
    except Exception as e:
        flash(f"Błąd pobierania usług: {e}")

    return render_template(
        "account_info.html",
        account=account,
        me_info=me_info,
        services=services,
    )
