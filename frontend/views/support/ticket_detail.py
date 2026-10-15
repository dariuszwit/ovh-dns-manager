from flask import render_template, request, redirect, url_for, flash, jsonify
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import support_bp


@support_bp.route("/detail/<int:ticket_id>", methods=["GET"])
@login_required
def ticket_detail(ticket_id):
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Nieprawidłowe konto OVH.")
        return redirect(url_for("frontend.support.select_account"))

    ticket = {}
    messages = []

    try:
        ticket = client.get(f'/support/tickets/{ticket_id}')
    except Exception as e:
        flash(f"Błąd pobierania zgłoszenia: {e}")

    try:
        msg_data = client.get(f'/support/tickets/{ticket_id}/messages')
        for item in msg_data:
            if isinstance(item, dict):
                messages.append(item)
            else:
                try:
                    msg = client.get(f'/support/tickets/{ticket_id}/messages/{item}')
                    messages.append(msg)
                except Exception as e:
                    messages.append({"messageId": item, "body": f"(nie udało się pobrać wiadomości: {e})"})
    except Exception as e:
        flash(f"Błąd pobierania wiadomości: {e}")

    # Sort messages chronologically
    messages.sort(key=lambda x: x.get('creationDate', ''))

    return render_template(
        "support_detail.html",
        account=account,
        ticket=ticket,
        ticket_id=ticket_id,
        messages=messages,
    )


@support_bp.route("/debug_messages/<int:ticket_id>", methods=["GET"])
@login_required
def debug_messages(ticket_id):
    """Temporary debug route — returns raw OVH API message data."""
    account = request.args.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    try:
        msg_data = client.get(f'/support/tickets/{ticket_id}/messages')
        sample = msg_data[:5] if isinstance(msg_data, list) else msg_data
        return jsonify({
            "msg_data_type": type(msg_data).__name__,
            "msg_data_sample": sample,
            "first_item_type": type(msg_data[0]).__name__ if msg_data else None,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@support_bp.route("/reply/<int:ticket_id>", methods=["POST"])
@login_required
def reply(ticket_id):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    body = request.form.get("body", "").strip()
    if not body:
        return jsonify({"error": "Treść wiadomości jest wymagana."}), 400

    try:
        client.post(f'/support/tickets/{ticket_id}/reply', body=body)
        return jsonify({"success": True, "message": "Odpowiedź wysłana."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@support_bp.route("/close/<int:ticket_id>", methods=["POST"])
@login_required
def close_ticket(ticket_id):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    try:
        client.post(f'/support/tickets/{ticket_id}/close')
        return jsonify({"success": True, "message": "Zgłoszenie zamknięte."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@support_bp.route("/reopen/<int:ticket_id>", methods=["POST"])
@login_required
def reopen_ticket(ticket_id):
    account = request.form.get("account")
    client = get_client(account)
    if client is None:
        return jsonify({"error": "Nieprawidłowe konto OVH."}), 400

    body = request.form.get("body", "").strip()
    if not body:
        return jsonify({"error": "Treść wiadomości jest wymagana."}), 400

    try:
        client.post(f'/support/tickets/{ticket_id}/reopen', body=body)
        return jsonify({"success": True, "message": "Zgłoszenie ponownie otwarte."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
