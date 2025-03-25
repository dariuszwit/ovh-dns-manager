from flask import render_template, session
from ..auth.decorators import login_required
from . import dashboard_bp

@dashboard_bp.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))
