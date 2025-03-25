from flask import Blueprint

# Tworzymy instancję Blueprint
records_bp = Blueprint('records', __name__)

# Importujemy widoki
from . import add_records, delete_records
