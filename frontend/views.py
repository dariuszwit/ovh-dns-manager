# frontend/views.py
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, session, flash
import ovh, json
from functools import wraps

frontend_bp = Blueprint('frontend', __name__)

# Helper functions do ładowania konfiguracji
def load_accounts():
    with open("ovh_accounts.json") as f:
        return json.load(f)["accounts"]

def load_users():
    with open("users.json") as f:
        return json.load(f)["users"]

# Dekorator autoryzacji
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('frontend.login'))
        return f(*args, **kwargs)
    return wrap

@frontend_bp.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        user = next((u for u in users if u["username"] == username and u["password"] == password), None)
        if user:
            session["username"] = user["username"]
            return redirect(url_for('frontend.dashboard'))
        else:
            error = "Invalid credentials"
    return render_template("login.html", error=error)

@frontend_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))

@frontend_bp.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for('frontend.login'))

# OVH client factory – tworzy instancję klienta dla danego konta
def get_client(account_name):
    accounts = load_accounts()
    account = next((a for a in accounts if a["name"] == account_name), None)
    if account is None:
        return None
    return ovh.Client(
        endpoint='ovh-eu',
        application_key=account["application_key"],
        application_secret=account["application_secret"],
        consumer_key=account["consumer_key"]
    )

@frontend_bp.route("/select_account", methods=["GET", "POST"])
@login_required
def select_account():
    accounts = load_accounts()
    if request.method == "POST":
        selected_account = request.form.get("account")
        if selected_account:
            return redirect(url_for("frontend.select_domain", account=selected_account))
    return render_template("select_account.html", accounts=accounts)

@frontend_bp.route("/select_domain")
@login_required
def select_domain():
    account = request.args.get("account")
    client = get_client(account)
    if client is None:
        flash("Invalid account selected.")
        return redirect(url_for("frontend.select_account"))
    try:
        domains = client.get('/domain')
    except Exception as e:
        flash(f"Error fetching domains: {e}")
        domains = []
    return render_template("select_domain.html", account=account, domains=domains)

@frontend_bp.route("/manage_domain/<domain>", methods=["GET", "POST"])
@login_required
def manage_domain(domain):
    account = request.args.get("account")
    client = get_client(account)
    if client is None:
        flash("Invalid account selected.")
        return redirect(url_for("frontend.select_account"))
    try:
        record_ids = client.get(f'/domain/zone/{domain}/record')
        records = [client.get(f'/domain/zone/{domain}/record/{rid}') for rid in record_ids]
    except Exception as e:
        flash(f"Error fetching records: {e}")
        records = []
    return render_template("manage_domain.html", account=account, domain=domain, records=records)

@frontend_bp.route("/delete_records/<domain>", methods=["POST"])
@login_required
def delete_records(domain):
    account = request.args.get("account")
    client = get_client(account)
    if client is None:
        flash("Invalid account selected.")
        return redirect(url_for("frontend.select_account"))
    
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
    return redirect(url_for("frontend.manage_domain", domain=domain, account=account))

@frontend_bp.route("/add_records/<domain>", methods=["POST"])
@login_required
def add_records(domain):
    account = request.args.get("account")
    client = get_client(account)
    if client is None:
        flash("Invalid account selected.")
        return redirect(url_for("frontend.select_account"))
    
    records_data = []
    try:
        count = int(request.form.get("number_of_records", 0))
    except:
        count = 0
    for i in range(count):
        rec_type = request.form.get(f"record_{i}_type")
        sub_domain = request.form.get(f"record_{i}_subDomain")
        target = request.form.get(f"record_{i}_target")
        ttl = request.form.get(f"record_{i}_ttl")
        if rec_type and target:
            record = {
                "fieldType": rec_type,
                "subDomain": sub_domain or "",
                "target": target,
                "ttl": int(ttl) if ttl and ttl.isdigit() else 3600
            }
            records_data.append(record)
    
    errors = []
    for record in records_data:
        try:
            client.post(f'/domain/zone/{domain}/record', record)
        except Exception as e:
            errors.append(f"Error adding record {record}: {e}")
    
    if errors:
        flash("Some errors occurred while adding records: " + "; ".join(errors))
    else:
        flash("New records added successfully.")
    return redirect(url_for("frontend.manage_domain", domain=domain, account=account))
