import flask


roles = flask.Blueprint('roles', __name__)

from . import views
