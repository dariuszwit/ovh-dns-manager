from flask import redirect, url_for, session
from . import auth_bp

@auth_bp.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("frontend.auth.login"))
