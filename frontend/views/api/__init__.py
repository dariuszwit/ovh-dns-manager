from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Importujemy klienta OVH
from . import ovh_client
