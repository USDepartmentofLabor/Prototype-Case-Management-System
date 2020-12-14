from flask import Blueprint

case_statuses = Blueprint('case_statuses', __name__)

from . import views
