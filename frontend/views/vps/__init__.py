from flask import Blueprint

vps_bp = Blueprint('vps', __name__)

from . import vps_list, vps_detail
