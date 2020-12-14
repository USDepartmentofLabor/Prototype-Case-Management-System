from flask import Blueprint


surveys = Blueprint('surveys', __name__)

from . import views

