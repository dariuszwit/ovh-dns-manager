from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import vps_bp


@vps_bp.route("/select_account", methods=["GET", "POST"])
@login_required
def select_account():
    from frontend.helpers.load_accounts import load_accounts
    accounts = load_accounts()

    if request.method == "POST":
        account = request.form.get("account")
        return redirect(url_for("frontend.vps.vps_list", account=account))

    return render_template("vps_select_account.html", accounts=accounts)


@vps_bp.route("/list", methods=["GET"])
@login_required
def vps_list():
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.vps.select_account"))

    servers = []
    try:
        vps_names = client.get('/vps')
        for vps_name in vps_names:
            try:
                vps_info = client.get(f'/vps/{vps_name}')
                servers.append(vps_info)
            except Exception:
                servers.append({"name": vps_name})
    except Exception as e:
        flash(f"Błąd pobierania serwerów VPS: {e}")

    return render_template("vps_list.html", account=account, servers=servers)
