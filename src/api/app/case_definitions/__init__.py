from flask import Blueprint


case_definitions = Blueprint('case_definitions', __name__)

from . import views