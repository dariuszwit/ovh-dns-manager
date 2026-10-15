from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import ssl_bp


@ssl_bp.route("/detail/<service_name>", methods=["GET"])
@login_required
def ssl_detail(service_name):
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.ssl.select_account"))

    cert_info = {}
    tasks = []
    dnssec_status = None

    try:
        cert_info = client.get(f'/ssl/{service_name}')
    except Exception as e:
        flash(f"Błąd pobierania certyfikatu SSL: {e}")

    try:
        task_ids = client.get(f'/ssl/{service_name}/tasks')
        for tid in task_ids[:10]:
            try:
                task_info = client.get(f'/ssl/{service_name}/tasks/{tid}')
                tasks.append(task_info)
            except Exception:
                tasks.append({"taskId": tid})
    except Exception:
        pass

    # Try to get DNSSEC status for the zone
    try:
        dnssec_status = client.get(f'/domain/zone/{service_name}/dnssec')
    except Exception:
        pass

    return render_template(
        "ssl_detail.html",
        account=account,
        service_name=service_name,
        cert_info=cert_info,
        tasks=tasks,
        dnssec_status=dnssec_status,
    )
