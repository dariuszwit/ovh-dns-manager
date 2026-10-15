from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import support_bp


@support_bp.route("/select_account", methods=["GET", "POST"])
@login_required
def select_account():
    from frontend.helpers.load_accounts import load_accounts
    accounts = load_accounts()

    if request.method == "POST":
        account = request.form.get("account")
        return redirect(url_for("frontend.support.ticket_list", account=account))

    return render_template("support_select_account.html", accounts=accounts)


@support_bp.route("/list", methods=["GET"])
@login_required
def ticket_list():
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.support.select_account"))

    tickets = []
    try:
        ticket_ids = client.get('/support/tickets', status='open')
        for tid in ticket_ids[:30]:
            try:
                t = client.get(f'/support/tickets/{tid}')
                tickets.append(t)
            except Exception:
                tickets.append({"ticketId": tid})
    except Exception:
        pass

    # Also get closed/resolved tickets (last 20)
    try:
        closed_ids = client.get('/support/tickets', status='closed')
        for tid in closed_ids[:20]:
            try:
                t = client.get(f'/support/tickets/{tid}')
                tickets.append(t)
            except Exception:
                tickets.append({"ticketId": tid, "state": "closed"})
    except Exception:
        pass

    # Sort by ticketId desc
    tickets.sort(key=lambda x: x.get('ticketId', 0), reverse=True)

    return render_template("support_list.html", account=account, tickets=tickets)
