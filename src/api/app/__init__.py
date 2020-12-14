from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_continuum import Continuum
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config import config
import flask_cloudy
from .services.eps_reporting_service import EPSReportingService
import flask_babel


def get_current_user():
    if session:
        return session.get('current_user_id', None)
    else:
        return None


db = SQLAlchemy()
continuum = Continuum(db=db, user_cls='User', current_user=get_current_user)
ma = Marshmallow()
jwt = JWTManager()
cors = CORS()
mail = Mail()
blacklist = set()
storage = flask_cloudy.Storage()
babel = flask_babel.Babel()


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'es', 'fr'])


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    continuum.init_app(app)
    storage.init_app(app)
    babel.init_app(app)

    app.reporting_service = EPSReportingService(app.config['DATA_DB_URI'])

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return jti in blacklist

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .users import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/users')

    from .surveys import surveys as surveys_blueprint
    app.register_blueprint(surveys_blueprint, url_prefix='/surveys')

    from .case_definitions import case_definitions as case_definitions_blueprint
    app.register_blueprint(case_definitions_blueprint, url_prefix='/case_definitions')

    from .cases import cases as cases_blueprint
    app.register_blueprint(cases_blueprint, url_prefix='/cases')

    from .case_statuses import case_statuses as case_statuses_blueprint
    app.register_blueprint(case_statuses_blueprint, url_prefix='/case_statuses')

    from .project import project as project_blueprint
    app.register_blueprint(project_blueprint, url_prefix='/project')

    from .roles import roles as roles_blueprint
    app.register_blueprint(roles_blueprint, url_prefix='/roles')

    from .activity_definitions import activity_definitions as activity_definitions_blueprint
    app.register_blueprint(activity_definitions_blueprint, url_prefix="/activity_definitions")

    from .activities import activities as activities_blueprint
    app.register_blueprint(activities_blueprint, url_prefix="/activities")

    return app
