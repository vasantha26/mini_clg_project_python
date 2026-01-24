from flask import Blueprint

bp = Blueprint('notices', __name__)

from . import routes
