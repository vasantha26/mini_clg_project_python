from flask import Blueprint

bp = Blueprint('timetable', __name__)

from . import routes
