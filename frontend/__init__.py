from flask import Blueprint, redirect

frontend_bp = Blueprint('frontend', __name__)

from .views.auth import auth_bp
from .views.dashboard import dashboard_bp
from .views.domain import domain_bp
from .views.records import records_bp
from .views.api import api_bp
from .views.hosting import hosting_bp
from .views.email import email_bp
from .views.ssl import ssl_bp
from .views.account import account_bp
from .views.vps import vps_bp
from .views.support import support_bp
from .views.billing import billing_bp

frontend_bp.register_blueprint(auth_bp, url_prefix="/auth")
frontend_bp.register_blueprint(dashboard_bp, url_prefix="/dashboard")
frontend_bp.register_blueprint(domain_bp, url_prefix="/domain")
frontend_bp.register_blueprint(records_bp, url_prefix="/records")
frontend_bp.register_blueprint(api_bp, url_prefix="/api")
frontend_bp.register_blueprint(hosting_bp, url_prefix="/hosting")
frontend_bp.register_blueprint(email_bp, url_prefix="/email")
frontend_bp.register_blueprint(ssl_bp, url_prefix="/ssl")
frontend_bp.register_blueprint(account_bp, url_prefix="/account")
frontend_bp.register_blueprint(vps_bp, url_prefix="/vps")
frontend_bp.register_blueprint(support_bp, url_prefix="/support")
frontend_bp.register_blueprint(billing_bp, url_prefix="/billing")

@frontend_bp.route("/")
def home():
    return redirect("/auth/")
