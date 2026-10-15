from flask import render_template, request, redirect, url_for, flash, jsonify
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import email_bp


@email_bp.route("/detail/<domain>", methods=["GET"])
@login_required
def email_detail(domain):
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.email.select_account"))

    domain_info = {}
    accounts_list = []
    redirections = []

    try:
        domain_info = client.get(f'/email/domain/{domain}')
    except Exception as e:
        flash(f"Błąd pobierania informacji o domenie: {e}")

    try:
        account_names = client.get(f'/email/domain/{domain}/account')
        for acc_name in account_names:
            try:
                acc_info = client.get(f'/email/domain/{domain}/account/{acc_name}')
                accounts_list.append(acc_info)
            except Exception:
                accounts_list.append({"accountName": acc_name})
    except Exception as e:
        flash(f"Błąd pobierania kont email: {e}")

    try:
        redir_ids = client.get(f'/email/domain/{domain}/redirection')
        for rid in redir_ids:
            try:
                redir_info = client.get(f'/email/domain/{domain}/redirection/{rid}')
                redirections.append(redir_info)
            except Exception:
                redirections.append({"id": rid})
    except Exception as e:
        flash(f"Błąd pobierania przekierowań email: {e}")

    return render_template(
        "email_detail.html",
        account=account,
        domain=domain,
        domain_info=domain_info,
        accounts_list=accounts_list,
        redirections=redirections,
    )


@email_bp.route("/create_account/<domain>", methods=["POST"])
@login_required
def create_account(domain):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    acc_name = request.form.get("accountName", "").strip()
    password = request.form.get("password", "").strip()
    description = request.form.get("description", "").strip()
    size = request.form.get("size", "5000000000")

    if not acc_name or not password:
        return jsonify({"error": "Nazwa konta i hasło są wymagane."}), 400

    try:
        client.post(f'/email/domain/{domain}/account', accountName=acc_name,
                     password=password, description=description, size=int(size))
        return jsonify({"success": True, "message": f"Konto {acc_name}@{domain} zostało utworzone."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@email_bp.route("/delete_account/<domain>/<acc_name>", methods=["POST"])
@login_required
def delete_account(domain, acc_name):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    try:
        client.delete(f'/email/domain/{domain}/account/{acc_name}')
        return jsonify({"success": True, "message": f"Konto {acc_name}@{domain} zostało usunięte."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@email_bp.route("/change_password/<domain>/<acc_name>", methods=["POST"])
@login_required
def change_password(domain, acc_name):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    password = request.form.get("password", "").strip()
    if not password:
        return jsonify({"error": "Hasło jest wymagane."}), 400

    try:
        client.post(f'/email/domain/{domain}/account/{acc_name}/changePassword',
                     password=password)
        return jsonify({"success": True, "message": f"Hasło dla {acc_name}@{domain} zostało zmienione."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@email_bp.route("/create_redirection/<domain>", methods=["POST"])
@login_required
def create_redirection(domain):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    from_addr = request.form.get("from", "").strip()
    to_addr = request.form.get("to", "").strip()
    local_copy = request.form.get("localCopy") == "true"

    if not from_addr or not to_addr:
        return jsonify({"error": "Oba adresy są wymagane."}), 400

    try:
        client.post(f'/email/domain/{domain}/redirection',
                     **{"from": from_addr, "to": to_addr, "localCopy": local_copy})
        return jsonify({"success": True, "message": f"Przekierowanie {from_addr} → {to_addr} utworzone."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@email_bp.route("/delete_redirection/<domain>/<int:redir_id>", methods=["POST"])
@login_required
def delete_redirection(domain, redir_id):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    try:
        client.delete(f'/email/domain/{domain}/redirection/{redir_id}')
        return jsonify({"success": True, "message": "Przekierowanie usunięte."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
