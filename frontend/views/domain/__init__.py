from flask import Blueprint

# GŁÓWNY blueprint dla domen
domain_bp = Blueprint('domain', __name__)

# Importujemy wszystkie widoki domenowe, które rejestrują endpointy
from . import select_account, select_domain, manage_domain
