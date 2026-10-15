from flask import render_template, request, redirect, url_for, flash, jsonify
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import vps_bp


@vps_bp.route("/detail/<vps_name>", methods=["GET"])
@login_required
def vps_detail(vps_name):
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.vps.select_account"))

    info = {}
    ips = []
    disks = []
    monitoring = {}

    try:
        info = client.get(f'/vps/{vps_name}')
    except Exception as e:
        flash(f"Błąd pobierania info VPS: {e}")

    try:
        ips = client.get(f'/vps/{vps_name}/ips')
    except Exception:
        pass

    try:
        disk_ids = client.get(f'/vps/{vps_name}/disks')
        for did in disk_ids:
            try:
                d = client.get(f'/vps/{vps_name}/disks/{did}')
                disks.append(d)
            except Exception:
                disks.append({"id": did})
    except Exception:
        pass

    try:
        monitoring = client.get(f'/vps/{vps_name}/monitoring',
                                period='lastday', type='cpu:used')
    except Exception:
        pass

    return render_template(
        "vps_detail.html",
        account=account,
        vps_name=vps_name,
        info=info,
        ips=ips,
        disks=disks,
        monitoring=monitoring,
    )


@vps_bp.route("/reboot/<vps_name>", methods=["POST"])
@login_required
def reboot(vps_name):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    try:
        client.post(f'/vps/{vps_name}/reboot')
        return jsonify({"success": True, "message": f"VPS {vps_name} restartowany."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@vps_bp.route("/start/<vps_name>", methods=["POST"])
@login_required
def start(vps_name):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    try:
        client.post(f'/vps/{vps_name}/start')
        return jsonify({"success": True, "message": f"VPS {vps_name} uruchomiony."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@vps_bp.route("/stop/<vps_name>", methods=["POST"])
@login_required
def stop(vps_name):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    try:
        client.post(f'/vps/{vps_name}/stop')
        return jsonify({"success": True, "message": f"VPS {vps_name} zatrzymany."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@vps_bp.route("/reinstall/<vps_name>", methods=["POST"])
@login_required
def reinstall(vps_name):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    template_id = request.form.get("templateId")
    if not template_id:
        return jsonify({"error": "Wybierz szablon systemu."}), 400

    try:
        client.post(f'/vps/{vps_name}/rebuild', imageId=int(template_id))
        return jsonify({"success": True, "message": f"Reinstalacja VPS {vps_name} zlecona."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@vps_bp.route("/available_images/<vps_name>", methods=["GET"])
@login_required
def available_images(vps_name):
    account = request.args.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    try:
        images = client.get(f'/vps/{vps_name}/images/available')
        return jsonify(images)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@vps_bp.route("/console/<vps_name>", methods=["GET"])
@login_required
def console(vps_name):
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.vps.select_account"))

    console_url = None
    try:
        result = client.post(f'/vps/{vps_name}/openConsoleAccess', protocol='VNCOverWebSocket')
        console_url = result.get('url')
    except Exception as e:
        flash(f"Błąd otwierania konsoli: {e}")

    return render_template(
        "vps_console.html",
        account=account,
        vps_name=vps_name,
        console_url=console_url,
    )
