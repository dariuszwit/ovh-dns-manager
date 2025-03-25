from flask import Blueprint

dashboard_bp = Blueprint('dashboard', __name__)

# Importujemy główny widok dashboardu
from . import dashboard
