from flask import render_template, request, redirect, url_for, flash, jsonify
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import support_bp


@support_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_ticket():
    account = request.args.get("account") or request.form.get("account")

    if request.method == "GET":
        if not account:
            return redirect(url_for("frontend.support.select_account"))

        client = get_client(account)
        if client is None:
            flash("Nieprawidłowe konto OVH.")
            return redirect(url_for("frontend.support.select_account"))

        # Get available services for the dropdown
        services = []
        try:
            svc_ids = client.get('/services')
            for sid in svc_ids[:50]:
                try:
                    svc = client.get(f'/services/{sid}')
                    name = svc.get('resource', {}).get('displayName',
                           svc.get('resource', {}).get('name', str(sid)))
                    services.append({"id": sid, "name": name})
                except Exception:
                    services.append({"id": sid, "name": str(sid)})
        except Exception:
            pass

        return render_template(
            "support_create.html",
            account=account,
            services=services,
        )

    # POST - submit new ticket
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    subject = request.form.get("subject", "").strip()
    body = request.form.get("body", "").strip()
    service_name = request.form.get("serviceName", "").strip()
    category = request.form.get("category", "assistance")

    if not subject or not body:
        return jsonify({"error": "Temat i treść są wymagane."}), 400

    try:
        params = {
            "subject": subject,
            "body": body,
            "type": category,
        }
        if service_name:
            params["serviceName"] = service_name

        result = client.post('/support/tickets/create', **params)
        ticket_id = result.get('ticketId', '')
        return jsonify({"success": True, "message": f"Zgłoszenie #{ticket_id} utworzone.",
                        "ticketId": ticket_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
