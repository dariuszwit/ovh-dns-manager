from flask import render_template, request, session, redirect, url_for, flash
from frontend.helpers.load_users import load_users
from . import auth_bp

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        user = next((u for u in users if u["username"] == username and u["password"] == password), None)
        if user:
            session["username"] = user["username"]
            return redirect(url_for('frontend.dashboard.dashboard'))  # Poprawione przekierowanie
        else:
            error = "Invalid credentials"
    return render_template("login.html", error=error)
