from flask import Blueprint

bp = Blueprint('fees', __name__)

from . import routes
