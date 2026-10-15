from flask import Blueprint

support_bp = Blueprint('support', __name__)

from . import ticket_list, ticket_detail, ticket_create
