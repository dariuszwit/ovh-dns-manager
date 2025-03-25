from flask import request, redirect, url_for, flash
from ..auth.decorators import login_required
from ..api.ovh_client import get_client
from . import records_bp

@records_bp.route("/delete_records/<domain>", methods=["POST"])
@login_required
def delete_records(domain):
    account = request.args.get("account")
    client = get_client(account)

    if client is None:
        flash("Invalid account selected.")
        return redirect(url_for("frontend.domain.select_account"))

    record_ids = request.form.getlist("record_ids")
    errors = []
    
    for rid in record_ids:
        try:
            client.delete(f'/domain/zone/{domain}/record/{rid}')
        except Exception as e:
            errors.append(f"Error deleting record {rid}: {e}")

    if errors:
        flash("Some errors occurred: " + "; ".join(errors))
    else:
        flash("Selected records deleted successfully.")

    return redirect(url_for("frontend.domain.manage_domain", domain=domain, account=account))
