from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import email_bp


@email_bp.route("/select_account", methods=["GET", "POST"])
@login_required
def select_account():
    from frontend.helpers.load_accounts import load_accounts
    accounts = load_accounts()

    if request.method == "POST":
        account = request.form.get("account")
        return redirect(url_for("frontend.email.email_list", account=account))

    return render_template("email_select_account.html", accounts=accounts)


@email_bp.route("/list", methods=["GET"])
@login_required
def email_list():
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.email.select_account"))

    email_domains = []
    try:
        email_domains = client.get('/email/domain')
    except Exception as e:
        flash(f"Błąd pobierania domen email: {e}")

    return render_template("email_list.html", account=account, email_domains=email_domains)
