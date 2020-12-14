from flask import Blueprint

activities = Blueprint('activities', __name__)

from . import views


