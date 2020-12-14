from flask import Blueprint

activity_definitions = Blueprint('activity_definitions', __name__)

from . import views
