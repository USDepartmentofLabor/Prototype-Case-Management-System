from werkzeug import http
from flask import jsonify, request, current_app, session, g
from .. import models
from . import surveys
from .. import db
from app import helpers
import flask_babel


@surveys.route('/', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_SURVEY,
    message=models.Permission.MSG_READ_SURVEY,
)
def get_surveys():
    current_app.logger.info(f"/surveys (get_surveys) accessed by {g.request_user.email}")

    updated_since = request.args.get('updated_since', None)
    updated_since = http.parse_date(updated_since)

    archived = request.args.get('archived', 'none')
    # archived
    #   all -> only archived surveys
    #   none -> only non-archived surveys
    #   any -> all surveys
    if archived and archived not in ['all', 'none', 'any']:
        msg = flask_babel.gettext(u"Unsupported archived filter : %(archived)s", archived=archived)
        return jsonify({'message': msg}), 400

    survey_query = models.Survey.query

    if archived in ('all', 'none'):
        is_archived = True if archived == 'all' else False
        survey_query = survey_query.filter_by(is_archived=is_archived)

    if updated_since:
        survey_query = survey_query.filter(models.Survey.updated_at >= updated_since)

    survey_list = survey_query.all()

    surveys_return = [s.__getstate__() for s in survey_list]
    return jsonify(surveys_return), 200


@surveys.route('/<int:survey_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_SURVEY,
    message=models.Permission.MSG_READ_SURVEY,
)
def get_survey(survey_id):
    current_app.logger.info(f"/surveys/{survey_id} GET accessed by {g.request_user.email}")

    survey = models.Survey.query.get_or_404(survey_id)
    return jsonify(survey.__getstate__()), 200


@surveys.route('/<int:survey_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_SURVEY,
    message=models.Permission.MSG_UPDATE_SURVEY,
)
def put_survey(survey_id):
    current_app.logger.info(f"/surveys/{survey_id} PUT accessed by {g.request_user.email}")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    survey = models.Survey.query.get_or_404(survey_id)

    put_survey_id = request.json.get('id', None)
    if not put_survey_id:
        msg = flask_babel.gettext("You must provide a survey id in your put object.")
        return jsonify({"message": msg}), 400
    if put_survey_id != survey.id:
        msg = flask_babel.gettext("The survey id in the URL does not match the survey id in your put object.")
        return jsonify({"message": msg}), 400

    requested_name = request.json.get('name', survey.name)
    if not requested_name:
        msg = flask_babel.gettext("Unable to figure out the name of your survey.")
        return jsonify({"message": msg}), 400

    if not requested_name[:1].isalpha():
        msg = flask_babel.gettext("The survey's name must start with a character.")
        return jsonify({"message": msg}), 400

    # check that the title is unique
    name_check = db.session.query(models.Survey).filter(
        models.Survey.name == requested_name, models.Survey.id != survey.id).all()
    if len(name_check):
        msg = flask_babel.gettext(
            "You have submitted a survey that has the same name as another survey. Survey names must be "
            "unique. Please change the survey name and resubmit."
        )
        return jsonify({"message": msg}), 400

    survey.name = requested_name
    survey.structure = request.json.get('structure', survey.structure)
    survey.is_archived = request.json.get('is_archived', survey.is_archived)
    db.session.commit()

    return jsonify(survey.__getstate__()), 200


@surveys.route('/<int:survey_id>/responses', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_SURVEY,
    message=models.Permission.MSG_READ_SURVEY,
)
def get_survey_responses(survey_id):
    current_app.logger.info(f"/surveys/{survey_id}/responses accessed by {g.request_user.email}")

    archived = request.args.get('archived', None)
    # archived
    #   all -> only archived surveys
    #   none -> only non-archived surveys
    #   any -> all surveys
    if archived and archived not in ['all', 'none', 'any']:
        msg = flask_babel.gettext(u"Unsupported archived filter : %(archived)s", archived=archived)
        return jsonify({'message': msg}), 400

    survey = models.Survey.query.get_or_404(survey_id)

    if archived == 'all':
        responses = models.SurveyResponse.query.filter_by(survey_id=survey.id, is_archived=True)
    elif archived is None or archived == 'none':
        responses = models.SurveyResponse.query.filter_by(survey_id=survey.id, is_archived=False)
    else:
        responses = models.SurveyResponse.query.filter_by(survey_id=survey.id)
    responses_return = []
    for response in responses:
        responses_return.append(response.__getstate__())
    return jsonify(responses_return), 200


@surveys.route('/<int:survey_id>/responses/<int:response_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_SURVEY,
    message=models.Permission.MSG_READ_SURVEY,
)
def get_survey_response(survey_id, response_id):
    current_app.logger.info(f"/surveys/{survey_id}/responses/{response_id} accessed by {g.request_user.email}")

    survey = models.Survey.query.get_or_404(survey_id)
    survey_response = models.SurveyResponse.query.filter_by(id=response_id, survey_id=survey_id).first_or_404()

    response = {
        'survey_id': survey_id,
        'survey_structure': survey.structure,
        **survey_response.__getstate__()
    }

    return jsonify(response), 200


@surveys.route('/', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CREATE_SURVEY,
    message=models.Permission.MSG_CREATE_SURVEY,
)
def post_survey():
    current_app.logger.info(f"/surveys (post_survey) accessed by {g.request_user.email}")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    current_app.logger.info(f"session['current_user_id'] == {session.get('current_user_id')}")

    # check that the request has the data required [survey_structure,
    # survey_name]
    if not request.json or 'structure' not in request.json:
        msg = flask_babel.gettext("The structure for your survey is missing.")
        return jsonify({"message": msg}), 400
    if not request.json or 'name' not in request.json:
        msg = flask_babel.gettext("The name for your survey is missing.")
        return jsonify({"message": msg}), 400
    survey_structure = request.get_json().get('structure', "")
    survey_name = request.get_json().get('name', "")
    if not survey_name:
        msg = flask_babel.gettext("Unable to figure out the name of your survey.")
        return jsonify({"message": msg}), 400

    if not survey_name[:1].isalpha():
        msg = flask_babel.gettext("The survey's name must start with a character.")
        return jsonify({"message": msg}), 400

    # check that the title is unique
    name_check = db.session.query(models.Survey).filter(
        models.Survey.name == survey_name).all()
    if len(name_check):
        msg = flask_babel.gettext(
            "You have submitted a survey that has the same name as another survey. Survey names must be "
            "unique. Please change the survey name and resubmit."
        )
        return jsonify({"message": msg}), 400

    # TODO: save reporting table name of survey
    # data_table_name = current_app.reporting_service.create_survey(survey_name, survey_structure, 'metabase_pg_user')

    # add the survey object
    new_survey = models.Survey(
        name=survey_name,
        reporting_table_name='',  # data_table_name,
        structure=survey_structure,
        created_by=g.request_user,
        updated_by=g.request_user
    )
    db.session.add(new_survey)
    db.session.commit()

    return jsonify(new_survey.__getstate__()), 200


@surveys.route('/<int:survey_id>/responses', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.SUBMIT_SURVEY,
    message=models.Permission.MSG_SUBMIT_SURVEY,
)
def post_survey_response(survey_id):
    current_app.logger.info(f"/surveys/{survey_id}/responses (POST) accessed by {g.request_user.email}")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    # check that the survey exists and get it
    survey = models.Survey.query.get_or_404(survey_id)

    # check that the request has the data required [response_structure]
    if not request.json or 'structure' not in request.json:
        msg = flask_babel.gettext("The structure for your survey response is missing.")
        return jsonify({"message": msg}), 400

    survey_structure = request.get_json().get('structure', '')
    if not survey_structure:
        msg = flask_babel.gettext("The structure for your survey response is missing.")
        return jsonify({"message": msg}), 400

    status_id = request.get_json().get('status_id', None)
    if status_id and not models.SurveyResponseStatus.is_valid_status(status_id):
        msg = flask_babel.gettext("The survey response status you provided is invalid.")
        return jsonify({"message": msg}), 400

    source_type = request.get_json().get('source_type', 'Standalone')
    if source_type not in ['Standalone', 'Case', 'Activity']:
        msg = flask_babel.gettext("The survey response source value you provided is invalid.")
        return jsonify({"message": msg}), 400

    # add the survey response object
    if status_id:
        status = models.SurveyResponseStatus.query.get(status_id)
        new_survey_response = models.SurveyResponse(
            structure=survey_structure,
            survey_id=survey.id,
            created_by=g.request_user,
            updated_by=g.request_user,
            status=status,
            source_type=source_type
        )
    else:
        new_survey_response = models.SurveyResponse(
            structure=survey_structure,
            survey_id=survey.id,
            created_by=g.request_user,
            updated_by=g.request_user,
            source_type=source_type
        )

    new_survey_response.source_type = request.get_json().get('source_type', None)
    new_survey_response.case_id = request.get_json().get('case_id', None)
    new_survey_response.activity_id = request.get_json().get('activity_id', None)

    created_location_data = helpers.parse_gps(request.get_json())
    if created_location_data.longitude is not None and created_location_data.latitude is not None:
        new_survey_response.created_location_coordinates = \
            f"POINT({created_location_data.longitude} {created_location_data.latitude})"
    new_survey_response.created_location_position_accuracy = created_location_data.position_accuracy
    new_survey_response.created_location_altitude = created_location_data.altitude
    new_survey_response.created_location_altitude_accuracy = created_location_data.altitude_accuracy
    new_survey_response.created_location_heading = created_location_data.heading
    new_survey_response.created_location_speed = created_location_data.speed
    new_survey_response.created_location_dt = created_location_data.location_dt

    db.session.add(new_survey_response)
    db.session.commit()

    current_app.reporting_service.create_response(survey, new_survey_response)

    return jsonify(new_survey_response.__getstate__()), 200


@surveys.route('/<int:survey_id>/responses/<int:response_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.SUBMIT_SURVEY,
    message=models.Permission.MSG_SUBMIT_SURVEY,
)
def put_survey_response(survey_id, response_id):
    current_app.logger.info(f"/surveys/{survey_id}/responses/{response_id} (PUT) accessed by {g.request_user.email}")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    _ = models.Survey.query.get_or_404(survey_id)
    response = models.SurveyResponse.query.get_or_404(response_id)

    survey_structure = request.get_json().get('structure', "")
    if not survey_structure:
        msg = flask_babel.gettext("The structure for your survey response is missing.")
        return jsonify({"message": msg}), 400

    status_id = request.get_json().get('status_id', None)
    if status_id and not models.SurveyResponseStatus.is_valid_status(status_id):
        msg = flask_babel.gettext("The survey response status you provided is invalid.")
        return jsonify({"message": msg}), 400

    if status_id:
        response.status_id = status_id

    source_type = request.get_json().get('source_type', None)
    if source_type and source_type not in ['Standalone', 'Case', 'Activity']:
        msg = flask_babel.gettext("The survey response source value you provided is invalid.")
        return jsonify({"message": msg}), 400

    if source_type:
        response.source_type = source_type

    location_data = helpers.parse_gps(request.get_json())
    if location_data.location_dt is not None:
        if location_data.longitude is not None and location_data.latitude is not None:
            response.updated_location_coordinates = \
                f"POINT({location_data.longitude} {location_data.latitude})"
        response.updated_location_position_accuracy = location_data.position_accuracy
        response.updated_location_altitude = location_data.altitude
        response.updated_location_altitude_accuracy = location_data.altitude_accuracy
        response.updated_location_heading = location_data.heading
        response.updated_location_speed = location_data.speed
        response.updated_location_dt = location_data.location_dt

    response.structure = survey_structure
    response.is_archived = request.json.get('is_archived', response.is_archived)
    response.updated_by = g.request_user
    db.session.commit()

    # TODO: update reporting DB

    return jsonify(response.__getstate__()), 200


@surveys.route('/<int:survey_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.DELETE_SURVEY,
    message=models.Permission.MSG_DELETE_SURVEY,
)
def delete_survey(survey_id):
    current_app.logger.info(f"/surveys/{survey_id} (DELETE) accessed by {g.request_user.email}")

    survey_to_delete = models.Survey.query.get_or_404(survey_id)

    for r in survey_to_delete.responses:
        db.session.delete(r)
        survey_to_delete.case_definitions = []

    db.session.delete(survey_to_delete)
    db.session.commit()

    msg = flask_babel.gettext("Survey successfully deleted.")
    return jsonify({"message": msg}), 200


@surveys.route('/<int:survey_id>/responses/<int:response_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.DELETE_SURVEY,
    message=models.Permission.MSG_DELETE_SURVEY,
)
def delete_survey_response(survey_id, response_id):
    current_app.logger.info(f"/surveys/{survey_id}/responses/{response_id} (DELETE) accessed by {g.request_user.email}")

    survey_of_response_to_delete = models.Survey.query.get_or_404(survey_id)
    response_to_delete = models.SurveyResponse.query.get_or_404(response_id)

    # TODO: update reporting DB to delete response

    db.session.delete(response_to_delete)
    db.session.commit()

    msg = flask_babel.gettext("Survey response successfully deleted.")
    return jsonify({"message": msg}), 200
