from flask import Blueprint

bp = Blueprint('marks', __name__)

from . import routes
