from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# Importujemy wszystkie widoki związane z autoryzacją
from . import login, logout, decorators
