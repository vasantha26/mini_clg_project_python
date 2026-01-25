from flask import Blueprint

bp = Blueprint('usermanagement', __name__)

from . import routes
