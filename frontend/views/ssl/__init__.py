from flask import Blueprint

ssl_bp = Blueprint('ssl', __name__)

from . import ssl_list, ssl_detail
