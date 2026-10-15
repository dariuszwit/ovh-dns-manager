from flask import render_template, request, redirect, url_for, flash, jsonify
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import hosting_bp


@hosting_bp.route("/detail/<hosting_name>", methods=["GET"])
@login_required
def hosting_detail(hosting_name):
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.hosting.select_account"))

    info = {}
    databases = []
    users_ftp = []

    try:
        info = client.get(f'/hosting/web/{hosting_name}')
    except Exception as e:
        flash(f"Błąd pobierania info o hostingu: {e}")

    try:
        db_names = client.get(f'/hosting/web/{hosting_name}/database')
        for db_name in db_names:
            try:
                db_info = client.get(f'/hosting/web/{hosting_name}/database/{db_name}')
                databases.append(db_info)
            except Exception:
                databases.append({"name": db_name})
    except Exception:
        pass

    try:
        ftp_users = client.get(f'/hosting/web/{hosting_name}/user')
        for ftp_user in ftp_users:
            try:
                user_info = client.get(f'/hosting/web/{hosting_name}/user/{ftp_user}')
                users_ftp.append(user_info)
            except Exception:
                users_ftp.append({"login": ftp_user})
    except Exception:
        pass

    return render_template(
        "hosting_detail.html",
        account=account,
        hosting_name=hosting_name,
        info=info,
        databases=databases,
        users_ftp=users_ftp,
    )


@hosting_bp.route("/change_ftp_password/<hosting_name>/<login>", methods=["POST"])
@login_required
def change_ftp_password(hosting_name, login):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    password = request.form.get("password", "").strip()
    if not password:
        return jsonify({"error": "Hasło jest wymagane."}), 400

    try:
        client.post(f'/hosting/web/{hosting_name}/user/{login}/changePassword',
                     password=password)
        return jsonify({"success": True, "message": f"Hasło FTP dla {login} zostało zmienione."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@hosting_bp.route("/restart/<hosting_name>", methods=["POST"])
@login_required
def restart_hosting(hosting_name):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    try:
        client.post(f'/hosting/web/{hosting_name}/request', action='reboot')
        return jsonify({"success": True, "message": f"Hosting {hosting_name} restartowany."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@hosting_bp.route("/dump_database/<hosting_name>/<db_name>", methods=["POST"])
@login_required
def dump_database(hosting_name, db_name):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    try:
        client.post(f'/hosting/web/{hosting_name}/database/{db_name}/dump',
                     date='now', sendEmail=True)
        return jsonify({"success": True, "message": f"Dump bazy {db_name} został zlecony. Otrzymasz email."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
