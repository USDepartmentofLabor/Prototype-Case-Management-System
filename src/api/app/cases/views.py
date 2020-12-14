from datetime import datetime
from flask import jsonify, request, current_app, g
from sqlalchemy import or_
from . import cases
from .cases_service import CasesService
from app import models, helpers, files, notes
import app
import flask_babel
from ..services import notification_service


# /cases GET
@cases.route('', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE,
    message=models.Permission.MSG_READ_CASE,
)
def get_cases():
    current_app.logger.info(f"/cases GET accessed by {g.request_user.email}")

    search_term = request.args.get('search_term', None)
    case_definition_id = request.args.get('case_definition_id', None)

    if search_term:
        current_app.logger.info(f"/cases GET searching cases for {search_term}")
        like_param = f"%{search_term}%"
        current_app.logger.info(f"/cases GET search like parameter = {like_param}")
        if case_definition_id:
            search_cases = models.Case.query.filter(models.Case.case_definition_id == case_definition_id,
                                                    or_(models.Case.name.ilike(like_param),
                                                        models.Case.key.ilike(like_param)))
        else:
            search_cases = models.Case.query.filter(
                or_(models.Case.name.ilike(like_param), models.Case.key.ilike(like_param)))
        return_cases = [c.__getstate__() for c in search_cases]
    elif case_definition_id:
        return_cases = [cd.__getstate__() for cd in
                        models.Case.query.filter(models.Case.case_definition_id == case_definition_id)]
    else:
        return_cases = [cd.__getstate__() for cd in models.Case.query.all()]

    return jsonify(return_cases), 200


@cases.route('/<int:case_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE,
    message=models.Permission.MSG_READ_CASE,
)
def get_case(case_id):
    current_app.logger.info(f"/cases/{case_id} GET accessed by {g.request_user.email}")

    case = models.Case.query.get_or_404(case_id)
    return jsonify(case.__getstate__()), 200


@cases.route('/<int:case_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_CASE,
    message=models.Permission.MSG_UPDATE_CASE,
)
def put_case(case_id):
    current_app.logger.info(f"/cases/{case_id} PUT accessed by {g.request_user.email}")

    case = models.Case.query.get_or_404(case_id)

    if 'name' in request.json.keys():
        cn = request.json.get('name', None)
        if not cn:
            msg = flask_babel.gettext("A name is required for a case.")
            return jsonify({"message": msg}), 400

        if len(cn) == 0:
            msg = flask_babel.gettext("A name is required for a case.")
            return jsonify({"message": msg}), 400

        if len(cn) < 8:
            msg = flask_babel.gettext("Case names must be at least 8 characters long.")
            return jsonify({"message": msg}), 400

        if len(cn) > 50:
            msg = flask_babel.gettext("Case names cannot be longer than 50 characters.")
            return jsonify({"message": msg}), 400

        name_check = app.db.session.query(models.Case).filter(
            models.Case.name == cn, models.Case.id != case.id).all()
        if len(name_check):
            msg = flask_babel.gettext("Case names must be unique.")
            return jsonify({"message": msg}), 400

        case.name = cn

    if 'status_id' in request.json:
        status_id = request.json['status_id']

        if not (g.request_user.can(models.Permission.ALLOW_TO_STATUS) or g.request_user.is_admin()):
            msg = flask_babel.gettext('You do not have permission to change a case\'s status')
            return jsonify({"message": msg}), 400

        if not models.CaseStatus.is_valid_status(status_id):
            msg = flask_babel.gettext("Invalid case status_id: %(status_id)s", status_id=status_id)
            return jsonify({"message": msg}), 400

        status = models.CaseStatus.query.get(status_id)

        if status.is_final and any(doc['id'] is None and doc['is_required'] for doc in case.documents):
            msg = flask_babel.gettext('All required case documents have not been uploaded.')
            return jsonify({"message": msg}), 400

        case.status_id = status_id
        case.status = status

    if 'description' in request.json.keys():
        case.description = request.json.get('description', case.description)

    send_assigned_to_notification = False
    if 'assigned_to_id' in request.json.keys():
        assigned_to_id = request.json.get('assigned_to_id', None)
        if assigned_to_id is not None:
            try:
                assigned_user = models.User.query.get(assigned_to_id)
                if assigned_user is None:
                    msg = flask_babel.gettext("Cannot assigned case to unknown user id.")
                    return jsonify({"message": msg}), 400

                if not (assigned_user.can(models.Permission.ASSIGNABLE_TO_CASE) or assigned_user.is_admin()):
                    msg = flask_babel.gettext("User does not have permission to be assigned to a case.")
                    return jsonify({"message": msg}), 400
            except:
                msg = flask_babel.gettext("Cannot assigned case to invalid user.")
                return jsonify({"message": msg}), 400
            send_assigned_to_notification = True

        case.assigned_to_id = assigned_to_id
        case.assigned_at = datetime.utcnow()

    location_data = helpers.parse_gps(request.get_json())
    if location_data.location_dt is not None:
        if location_data.longitude is not None and location_data.latitude is not None:
            case.updated_location_coordinates = \
                f"POINT({location_data.longitude} {location_data.latitude})"
        case.updated_location_position_accuracy = location_data.position_accuracy
        case.updated_location_altitude = location_data.altitude
        case.updated_location_altitude_accuracy = location_data.altitude_accuracy
        case.updated_location_heading = location_data.heading
        case.updated_location_speed = location_data.speed
        case.updated_location_dt = location_data.location_dt

    if app.db.session.is_modified(case):
        case.updated_by = g.request_user
        app.db.session.commit()

    current_app.reporting_service.update_case_row(case)
    if send_assigned_to_notification:
        notification_service.notify_user_they_were_assigned_a_case(case)

    return jsonify(case.__getstate__()), 200


@cases.route('/<int:case_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.DELETE_CASE,
    message=models.Permission.MSG_DELETE_CASE,
    admin_allowed=True
)
def delete_case(case_id):
    current_app.logger.info(f"/cases/{case_id} DELETE accessed by {g.request_user.email}")

    case = models.Case.query.get_or_404(case_id)
    current_app.reporting_service.delete_case_row(case.case_definition.reporting_table_name, case.id)
    for n in case.notes:
        app.db.session.delete(n)
    for f in case.files:
        app.db.session.delete(f)
    for r in case.responses:
        app.db.session.delete(r)
    app.db.session.delete(case)
    app.db.session.commit()
    msg = flask_babel.gettext("Case successfully deleted.")
    return jsonify({"message": msg}), 200


@cases.route('/<int:case_id>/surveys/<int:survey_id>/responses', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_SURVEY,
    message=models.Permission.MSG_READ_SURVEY,
    admin_allowed=True
)
def get_case_survey_responses(case_id, survey_id):
    survey = models.Survey.query.get_or_404(survey_id)
    responses = survey.responses.filter_by(case_id=case_id).all()

    return jsonify([r.__getstate__() for r in responses]), 200


@cases.route('/<int:case_id>/custom_fields/<string:custom_field_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_CASE,
    message=models.Permission.MSG_UPDATE_CASE,
)
def put_case_custom_field(case_id, custom_field_id):
    current_app.logger.info(f"/cases/{case_id}/custom_fields/{custom_field_id} PUT accessed by {g.request_user.email}")

    case = models.Case.query.get_or_404(case_id, description=flask_babel.gettext("Case ID was not found"))
    if not case.has_custom_field(custom_field_id):
        msg = flask_babel.gettext("The case's custom field was not found")
        return jsonify({'message': msg}), 404

    service = CasesService(json_args=request.get_json())
    return service.update_custom_field(case, custom_field_id)


@cases.route('/<int:case_id>/custom_fields/<string:custom_field_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE,
    message=models.Permission.MSG_READ_CASE,
)
def get_case_custom_field(case_id, custom_field_id):
    current_app.logger.info(f"/cases/{case_id}/custom_fields/{custom_field_id} GET accessed by {g.request_user.email}")

    case = models.Case.query.get_or_404(case_id, description=flask_babel.gettext("Case ID was not found"))
    if not case.has_custom_field(custom_field_id):
        msg = flask_babel.gettext("The case's custom field was not found")
        return jsonify({'message': msg}), 404

    service = CasesService(json_args=request.get_json())
    return service.get_custom_field(case, custom_field_id)


@cases.route('/<int:case_id>/custom_fields', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE,
    message=models.Permission.MSG_READ_CASE,
)
def get_cases_custom_field(case_id):
    current_app.logger.info(f"/cases/{case_id}/custom_fields GET accessed by {g.request_user.email}")

    case = models.Case.query.get_or_404(case_id, description=flask_babel.gettext("Case ID was not found"))

    return jsonify(case.custom_fields), 200


@cases.route('/<int:case_id>/add_file', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_CASE,
    message=models.Permission.MSG_UPDATE_CASE,
)
def post_case_file(case_id):
    current_app.logger.info(f"/cases/{case_id}/add_file POST accessed by {g.request_user.email}")

    case = models.Case.query.get_or_404(case_id)
    return files.post(case.id, "Case")


@cases.route('/files/<int:file_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE,
    message=models.Permission.MSG_READ_CASE,
)
def get_case_file(file_id):
    current_app.logger.info(f"/cases/files/{file_id} GET accessed by {g.request_user.email}")
    return files.get(file_id)


# TODO DELETE /cases/files/<int: case_file_id>
@cases.route('files/<int:file_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_CASE,
    message=models.Permission.MSG_UPDATE_CASE,
)
def delete_case_file(file_id):
    current_app.logger.info(f"/cases/files/{file_id} DELETE accessed by {g.request_user.email}")
    return files.delete(file_id)


@cases.route('/files/<int:file_id>/download', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE,
    message=models.Permission.MSG_READ_CASE,
)
def download_case_file(file_id):
    current_app.logger.info(f"/cases/files/{file_id}/download GET accessed by {g.request_user.email}")
    return files.download(file_id)


@cases.route('/<int:case_id>/notes', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_CASE,
    message=models.Permission.MSG_UPDATE_CASE,
)
def post_case_note(case_id):
    current_app.logger.info(f"/cases/{case_id}/notes POST accessed by {g.request_user.email}")

    case = models.Case.query.get_or_404(case_id)
    return notes.post(case.id, 'Case')


@cases.route('/<int:case_id>/notes', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE,
    message=models.Permission.MSG_READ_CASE,
)
def get_case_notes(case_id):
    current_app.logger.info(f"/cases/{case_id}/notes GET accessed by {g.request_user.email}")
    case = models.Case.query.get_or_404(case_id)
    return jsonify([n.__getstate__() for n in case.notes]), 200


@cases.route('/<int:case_id>/notes/<int:note_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE,
    message=models.Permission.MSG_READ_CASE,
)
def get_case_note(case_id, note_id):
    current_app.logger.info(f"/cases/{case_id}/notes/{note_id} GET accessed by {g.request_user.email}")
    _ = models.Case.query.get_or_404(case_id)
    return notes.get(note_id)


@cases.route('/<int:case_id>/notes/<int:note_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_CASE,
    message=models.Permission.MSG_UPDATE_CASE,
)
def put_case_note(case_id, note_id):
    current_app.logger.info(f"/cases/{case_id}/notes/{note_id} PUT accessed by {g.request_user.email}")
    _ = models.Case.query.get_or_404(case_id)

    return notes.put(note_id)


@cases.route('/<int:case_id>/notes/<int:note_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_CASE,
    message=models.Permission.MSG_UPDATE_CASE,
)
def delete_case_note(case_id, note_id):
    current_app.logger.info(f"/cases/{case_id}/notes/{note_id} DELETE accessed by {g.request_user.email}")

    _ = models.Case.query.get_or_404(case_id)
    return notes.delete(note_id)
