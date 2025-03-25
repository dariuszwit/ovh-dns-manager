from flask import render_template, request, redirect, url_for, flash
from ..auth.decorators import login_required
from frontend.helpers.load_accounts import load_accounts
from . import domain_bp

@domain_bp.route("/select_account", methods=["GET", "POST"])
@login_required
def select_account():
    accounts = load_accounts()
    if request.method == "POST":
        selected_account = request.form.get("account")
        if selected_account:
            # Używamy pełnej ścieżki do endpointu, bo blueprinty są zagnieżdżone
            return redirect(url_for("frontend.domain.select_domain", account=selected_account))
    return render_template("select_account.html", accounts=accounts)
