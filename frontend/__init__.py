from flask import Blueprint, redirect

frontend_bp = Blueprint('frontend', __name__)

from .views.auth import auth_bp
from .views.dashboard import dashboard_bp
from .views.domain import domain_bp
from .views.records import records_bp
from .views.api import api_bp

frontend_bp.register_blueprint(auth_bp, url_prefix="/auth")
frontend_bp.register_blueprint(dashboard_bp, url_prefix="/dashboard")
frontend_bp.register_blueprint(domain_bp, url_prefix="/domain")
frontend_bp.register_blueprint(records_bp, url_prefix="/records")
frontend_bp.register_blueprint(api_bp, url_prefix="/api")

@frontend_bp.route("/")
def home():
    return redirect("/auth/")
