from flask import Blueprint

bp = Blueprint('students', __name__)

from . import routes
