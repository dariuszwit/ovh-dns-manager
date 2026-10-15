from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import ssl_bp


@ssl_bp.route("/select_account", methods=["GET", "POST"])
@login_required
def select_account():
    from frontend.helpers.load_accounts import load_accounts
    accounts = load_accounts()

    if request.method == "POST":
        account = request.form.get("account")
        return redirect(url_for("frontend.ssl.ssl_list", account=account))

    return render_template("ssl_select_account.html", accounts=accounts)


@ssl_bp.route("/list", methods=["GET"])
@login_required
def ssl_list():
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.ssl.select_account"))

    certificates = []
    try:
        cert_ids = client.get('/ssl')
        for cert_id in cert_ids:
            try:
                cert_info = client.get(f'/ssl/{cert_id}')
                certificates.append(cert_info)
            except Exception:
                certificates.append({"serviceName": cert_id})
    except Exception as e:
        flash(f"Błąd pobierania certyfikatów SSL: {e}")

    return render_template("ssl_list.html", account=account, certificates=certificates)
