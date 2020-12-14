import sys
import time

import jwt
from werkzeug import http
from flask import jsonify, current_app, g, request
import flask_babel
import sqlalchemy
from sqlalchemy_continuum import version_class, Operation
from app import models
from app.main import main
from app import db, helpers, metabase
import app


@main.route('/', methods=['GET'])
def default_response():
    current_app.logger.info(f"/ accessed")

    msg = flask_babel.gettext("I'm here")
    return jsonify({'message': msg})


@main.route('/secure', methods=['GET'])
@helpers.jwt_auth
def default_secure():
    current_app.logger.info(f"/secure accessed {g.request_user.username}")

    msg = flask_babel.gettext('Hi %(email)s', email=g.request_user.email)
    return jsonify({'message': msg})


@main.route('/lookups', methods=['GET'])
@helpers.jwt_auth
def get_lookup_values():
    current_app.logger.info(f"/lookups accessed {g.request_user.username}")

    roles = [r.__getstate__() for r in models.Role.query.all()]
    survey_response_statuses = [s.__getstate__() for s in models.SurveyResponseStatus.query.all()]
    case_statuses = [c.__getstate__() for c in models.CaseStatus.query.all()]

    permissions = models.Permission.get_as_list()

    return jsonify({
        "roles": roles,
        "survey_response_statuses": survey_response_statuses,
        "case_statuses": case_statuses,
        "permissions": permissions
    }), 200


@main.route('/configuration', methods=['GET'])
@helpers.jwt_auth
def get_configuration():
    current_app.logger.info(f"/configuration accessed {g.request_user.email}")

    return jsonify({
        'metabase_url': current_app.config['METABASE_URL'],
        'api_version': current_app.config['API_VERSION'],
    }), 200


@main.route('/dashboards', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CONFIGURE_SYSTEM,
    message=models.Permission.MSG_CONFIGURE_SYSTEM,
)
def get_dashboards():
    current_app.logger.info(f"/dashboards accessed {g.request_user.email}")

    dashboards = metabase.get_dashboards()

    return jsonify(dashboards), 200


@main.route('/dashboards/set-default', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CONFIGURE_SYSTEM,
    message=models.Permission.MSG_CONFIGURE_SYSTEM,
)
def set_default_dashboard():
    current_app.logger.info(f"/dashboards/set-default {g.request_user.email}")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    dashboard_id = request.json.get('dashboard_id', None)

    default_dashboard = models.EPSProperty.query.filter_by(property='default_dashboard_id').first()
    if default_dashboard is None:
        default_dashboard = models.EPSProperty(property='default_dashboard_id', value=dashboard_id)
        db.session.add(default_dashboard)
    else:
        default_dashboard.value = dashboard_id
    db.session.commit()

    dashboards = metabase.get_dashboards()

    return jsonify(dashboards), 200


@main.route('/dashboards/get-default', methods=['GET'])
@helpers.jwt_auth
def get_default_dashboard():
    current_app.logger.info(f"/dashboards/get-default accessed {g.request_user.email}")

    default_dashboard = models.EPSProperty.query.filter_by(property='default_dashboard_id').first()
    if default_dashboard:
        default_dashboard_id = default_dashboard.value_as_int()
        payload = {
            "resource": {"dashboard": default_dashboard_id},
            "params": {},
            "exp": round(time.time()) + (60 * 10)  # 10 minute expiration
        }
        token = jwt.encode(payload, current_app.config['METABASE_SECRET_KEY'], algorithm="HS256")
        default_dashboard_url = f"{current_app.config['METABASE_URL']}/embed/dashboard/{token.decode('utf8')}#bordered=true&titled=true"
    else:
        default_dashboard_id = None
        default_dashboard_url = None

    return jsonify({
        'default_dashboard_id': default_dashboard_id,
        'default_dashboard_url': default_dashboard_url
    }), 200


@main.route('/deleted', methods=['GET'])
@helpers.jwt_auth
def get_deleted():
    current_app.logger.info(f"/deleted accessed {g.request_user.email}")

    deleted_since = request.args.get('deleted_since', None)
    deleted_since = http.parse_date(deleted_since)

    deleted_objects = {
        "surveys": [],
        "responses": [],
        "case_definitions": [],
        "cases": []
    }

    endpoints = [
        {
            'name': 'surveys',
            'model': models.Survey,
        },
        {
            'name': 'responses',
            'model': models.SurveyResponse,
        },
        {
            'name': 'case_definitions',
            'model': models.CaseDefinition,
        },
        {
            'name': 'cases',
            'model': models.Case,
        },
        {
            'name': 'activities',
            'model': models.Activity
        },
        {
            'name': 'activity_definitions',
            'model': models.ActivityDefinition
        }
    ]

    def gen_item(item):
        return {'id': item.id, 'deleted_at': item.transaction.issued_at.isoformat()}

    for e in endpoints:
        model_version_class = version_class(e['model'])
        query = app.db.session.query(model_version_class)

        query = query.filter_by(operation_type=Operation.DELETE)

        deleted = query.all()

        if deleted_since:
            deleted = [i for i in deleted if i.transaction.issued_at >= deleted_since]

        deleted_objects[e['name']] = [gen_item(d) for d in deleted]

    return jsonify(deleted_objects), 200


@main.route('/reset-reporting', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.RESET_REPORTING,
    message=models.Permission.MSG_RESET_REPORTING,
)
def reset_reporting():
    current_app.logger.info(f"/reset-reporting accessed by {g.request_user.email}")

    try:
        current_app.logger.info("/reset-reporting: deleting all tables in reporting database")
        current_app.reporting_service.delete_all()
        current_app.logger.info("/reset-reporting: re-creating all tables in reporting database")

        current_app.logger.info("/reset-reporting: re-creating all survey tables")
        for survey in models.Survey.query.all():

            current_app.logger.info(f"/reset-reporting: re-creating table for survey {survey.name}")

            current_app.reporting_service.create_survey(survey, 'metabase_pg_user')

            for response in survey.responses:
                current_app.reporting_service.create_response(survey, response)

        current_app.logger.info("/reset-reporting: re-creating all case tables")
        for case_definition in models.CaseDefinition.query.all():
            current_app.logger.info(f"/reset-reporting: re-creating table for case definition {case_definition.name}")

            case_definition.reporting_table_name = current_app.reporting_service.create_case_table(case_definition)
            app.db.session.commit()

            for case in case_definition.cases:
                current_app.reporting_service.add_case_row(case)

    except sqlalchemy.exc.ProgrammingError as err:
        current_app.logger.error(f"/reset-reporting error resetting reporting database : {err}")
    except:
        current_app.logger.error(f"/reset-reporting error resetting reporting database : {sys.exc_info()[0]}")

    return '', 204
