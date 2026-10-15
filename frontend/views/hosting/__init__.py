from flask import Blueprint

hosting_bp = Blueprint('hosting', __name__)

from . import hosting_list, hosting_detail
