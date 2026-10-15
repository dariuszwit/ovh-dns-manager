from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import hosting_bp


@hosting_bp.route("/select_account", methods=["GET", "POST"])
@login_required
def select_account():
    from frontend.helpers.load_accounts import load_accounts
    accounts = load_accounts()

    if request.method == "POST":
        account = request.form.get("account")
        return redirect(url_for("frontend.hosting.hosting_list", account=account))

    return render_template("hosting_select_account.html", accounts=accounts)


@hosting_bp.route("/list", methods=["GET"])
@login_required
def hosting_list():
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.hosting.select_account"))

    hostings = []
    try:
        hostings = client.get('/hosting/web')
    except Exception as e:
        flash(f"Błąd pobierania hostingów: {e}")

    return render_template("hosting_list.html", account=account, hostings=hostings)
