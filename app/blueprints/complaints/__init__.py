from flask import Blueprint

bp = Blueprint('complaints', __name__)

from . import routes
